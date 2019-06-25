# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an ESRS instances"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import https_to_port, get_ipv4_addrs


@click.command()
@click.option('-i', '--image', default='3.28', show_default=True,
              help='The version of ESRS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ESRS instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new ESRS instance to')
@click.pass_context
def esrs(ctx, name, image, external_network):
    """Create an instance of ESRS"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/esrs',
                        message='Creating a new instance of ESRS running {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        vm_type = data['meta']['component']
        https_port = https_to_port(vm_type.lower())
        with Spinner('Creating an SSH and HTTPS port mapping rules'):
            for ipv4 in ipv4_addrs:
                portmap_payload = {'target_addr' : ipv4, 'target_port' : 22,
                                   'target_name' : name, 'target_component' : vm_type}
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

                portmap_payload['target_port'] = https_port
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect esrs --name {}' to access your new ESRS instance".format(name))
