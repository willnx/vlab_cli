# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a CentOS instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_ipv4_addrs
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='7', show_default=True,
              help='The version of CentOS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CentOS instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new CentOS instance to')
@click.pass_context
def centos(ctx, name, image, external_network):
    """Create an instance of CentOS"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/centos',
                        message='Creating new instance of CentOS {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        vm_type = data['meta']['component']
        with Spinner('Creating an SSH port mapping rule'):
            for ipv4 in ipv4_addrs:
                ctx.obj.vlab_api.map_port(target_addr=ipv4, target_port=22,
                                          target_name=name, target_component=vm_type)
    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect centos --name {}' to access your new CentOS instance".format(name))
