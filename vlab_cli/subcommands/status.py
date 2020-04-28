# -*- coding: UTF-8 -*-
"""
Defines the CLI for a little status page of your vLab inventory
"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter, Spinner, to_timestamp


@click.command()
@click.pass_context
def status(ctx):
    """Display general information about your virtual lab"""
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/inventory',
                        message='Collecting information about your inventory',
                        method='GET',
                        timeout=120)
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
        vm_header = ['Name', 'IPs', 'Connectable', 'Type', 'Version', 'Powered', 'Networks']
        for vm in sorted(vm_info.keys()):
            params = {'name' : vm}
            resp = ctx.obj.vlab_api.get('/api/1/ipam/addr', params=params, auto_check=False)
            if resp.json()['error'] == None:
                addr_info = resp.json()['content']
            else:
                addr_info = {}
            connectable = addr_info.get(vm, {}).get('routable', 'initializing')
            networks = ','.join(vm_info[vm].get('networks', ['?']))
            kind = vm_info[vm]['meta']['component']
            version = vm_info[vm]['meta']['version']
            power = vm_info[vm]['state'].replace('powered', '')
            ips = '\n'.join(vm_info[vm]['ips'])
            if not ips:
                # fall back to port map rule
                addrs = addr_info.get(vm, {}).get('addr', '')
                ips = '\n'.join(addrs)
            row = [vm, ips, connectable, kind, version, power, networks]
            vm_body.append(row)

        quota_info = ctx.obj.vlab_api.get('/api/1/quota').json()['content']


    heading = '\nUsername: {}\nGateway : {}\nVM Quota: {}\nVM Count: {}'.format(ctx.obj.username,
                                                                                  gateway_ip,
                                                                                  quota_info['soft-limit'],
                                                                                  len(vm_info.keys()))
    vm_table = tabulate(vm_body, headers=vm_header, tablefmt='presto')
    click.echo(heading)
    if len(vm_info.keys()) > quota_info['soft-limit']:
        click.secho('\n\t!!!WARNING!!! Currently exceeding VM quota limit!\n', bold=True)
    if quota_info['exceeded_on']:
        exp_date = quota_info['exceeded_on'] + quota_info['grace_period']
        quota_warning = '\tQuota Exceeded on: {}\n'.format(to_timestamp(quota_info['exceeded_on']))
        quota_warning += '\tAutomatic VM deletion will occur on: {}\n'.format(to_timestamp(exp_date))
        click.secho(quota_warning, bold=True)

    if vm_body:
        click.echo('\nMachines:\n\n{}\n'.format(vm_table))
    else:
        typewriter("Looks like there's nothing in your lab.")
        typewriter("Use 'vlab create -h' to start deploying some machines")
