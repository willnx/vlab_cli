# -*- coding: UTF-8 -*-
"""
Defines the CLI for a little status page of your vLab inventory
"""
import time
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task


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
            gateway_ip = None
    else:
        gateway_ip = None
    vm_body = []
    vm_header = ['Name', 'IPs', 'Type', 'Version', 'Powered', 'Console']
    for vm, data in vm_info.items():
        shorter_link = ctx.obj.vlab_api.post('/api/1/link',
                                             json={'url': data['console']}).json()['content']['url']
        kind = data['meta']['component']
        version = data['meta']['version']
        power = data['state'].replace('powered', '')
        row = [vm, '\n'.join(data['ips']), kind, version, power, shorter_link]
        vm_body.append(row)

    heading = '\nUsername: {}\nGateway : {}\n'.format(ctx.obj.username, gateway_ip)
    vm_table = tabulate(vm_body, headers=vm_header, tablefmt='presto')
    click.echo(heading)
    click.echo('Machines:\n\n{}\n'.format(vm_table))
