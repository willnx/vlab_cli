# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Windows Desktop client"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_ipv4_addrs
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='10', show_default=True,
              help='The version of Windows to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Windows client in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new Windows client to')
@click.pass_context
def windows(ctx, name, image, external_network):
    """Create a new Windows Desktop client"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/windows',
                        message='Creating a new instance of Windows {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        vm_type = data['meta']['component']
        with Spinner('Creating an RDP port mapping rule'):
            for ipv4 in ipv4_addrs:
                portmap_payload = {'target_addr' : ipv4, 'target_port' : 3389,
                                   'target_name' : name, 'target_component' : vm_type}
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect windows --name {}' to access your new Windows client".format(name))
