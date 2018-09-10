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
def info(ctx):
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
    jumpbox = vm_info.pop('jumpBox', None)
    if jumpbox:
        jumpbox_ip = ' '.join(jumpbox['ips'])
    else:
        jumpbox_ip = None
    vm_body = []
    vm_header = ['Name', 'IPs', 'Type', 'Version', 'Console']
    for vm, data in vm_info.items():
        shorter_link = ctx.obj.vlab_api.post('/api/1/link',
                                             json={'url': data['console']}).json()['content']['url']
        try:
            kind, version = data['note'].split('=')
        except:
            kind, version = None, None
        row = [vm, '\n'.join(data['ips']), kind, version, shorter_link]
        vm_body.append(row)

    heading = '\nUsername: {}\nGateway : {}\nJumpBox : {}\n'.format(ctx.obj.username, gateway_ip, jumpbox_ip)
    vm_table = tabulate(vm_body, headers=vm_header, tablefmt='presto')
    click.echo(heading)
    click.echo('Machines:\n\n{}\n'.format(vm_table))
