# -*- coding: UTF-8 -*-
"""
Defines the CLI for a little status page of your vLab inventory
"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter, Spinner


@click.command()
@click.pass_context
def status(ctx):
    """Display general information about your virtual lab"""
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/inventory',
                        message='Collecting information about your inventory',
                        method='GET')
    vm_info = resp.json()['content']
    gateway = vm_info.pop('defaultGateway', None)
    if gateway:
        try:
            # if the gateway is off, it wont have an IP
            gateway_ip = [x for x in gateway['ips'] if ':' not in x and not x.startswith('192.168')][0]
        except IndexError:
            gateway_ip = gateway['state']
    else:
        gateway_ip = 'None' # so users see the literal word
    with Spinner('Processing inventory records'):
        vm_body = []
        vm_header = ['Name', 'IPs', 'Connectable', 'Type', 'Version', 'Powered', 'Console']
        for vm in sorted(vm_info.keys()):
            params = {'name' : vm}
            addr_info = ctx.obj.vlab_api.get('/api/1/ipam/addr', params=params).json()['content']
            connectable = addr_info.get(vm, {}).get('routable', 'initializing')
            shorter_link = ctx.obj.vlab_api.post('/api/1/link',
                                                 json={'url': vm_info[vm]['console']}).json()['content']['url']
            kind = vm_info[vm]['meta']['component']
            version = vm_info[vm]['meta']['version']
            power = vm_info[vm]['state'].replace('powered', '')
            ips = '\n'.join(vm_info[vm]['ips'])
            if not ips:
                # fall back to port map rule
                addrs = addr_info.get(vm, {}).get('addr', '')
                ips = '\n'.join(addrs)
            row = [vm, ips, connectable, kind, version, power, shorter_link]
            vm_body.append(row)

    heading = '\nUsername: {}\nGateway : {}\n'.format(ctx.obj.username, gateway_ip)
    vm_table = tabulate(vm_body, headers=vm_header, tablefmt='presto')
    click.echo(heading)
    if vm_body:
        click.echo('Machines:\n\n{}\n'.format(vm_table))
    else:
        typewriter("Looks like there's nothing in your lab.")
        typewriter("Use 'vlab create -h' to start deploying some machines")
