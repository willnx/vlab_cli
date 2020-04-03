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
@click.option('--desktop', is_flag=True, show_default=True,
              help='Deploy the VM with a GUI')
@click.option('-p', '--cpu-count', default='4', type=click.Choice(['4', '8', '12']),
              help='The number of CPU cores to allocate to the VM')
@click.option('-r', '--ram', default='4', type=click.Choice(['4', '6', '8']),
              help='The number of GB of RAM/memory to allocate')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new CentOS instance to')
@click.pass_context
def centos(ctx, name, image, external_network, desktop, cpu_count, ram):
    """Create an instance of CentOS"""
    body = {'network': external_network,
            'name': name,
            'image': image,
            'desktop': desktop,
            'ram': int(ram),
            'cpu-count': int(cpu_count)}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/centos',
                        message='Creating a new instance of CentOS {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        vm_type = data['meta']['component']
        with Spinner('Creating an SSH port mapping rule'):
            for ipv4 in ipv4_addrs:
                portmap_payload = {'target_addr' : ipv4, 'target_port' : 22,
                                   'target_name' : name, 'target_component' : vm_type}
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)
        if desktop:
            with Spinner('Creating an RDP port mapping rule'):
                for ipv4 in ipv4_addrs:
                    portmap_payload = {'target_addr' : ipv4, 'target_port' : 3389,
                                       'target_name' : name, 'target_component' : vm_type}
                    ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect centos --name {}' to access your new CentOS instance".format(name))
