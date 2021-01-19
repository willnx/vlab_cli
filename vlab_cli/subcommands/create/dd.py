# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Data Domain server"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import https_to_port, get_ipv4_addrs


@click.command()
@click.option('-i', '--image', default='7.4.0.5', show_default=True,
              help='The version of Data Domain server to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Data Domain server in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new Data Domain server to')
@click.pass_context
def dd(ctx, name, image, external_network):
    """Create a Data Domain server"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/data-domain',
                        message='Creating a new Data Domain server running {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        with Spinner("Creating port mapping rules for HTTPS and SSH"):
            vm_type = data['meta']['component']
            https_port = https_to_port(vm_type.lower())
            portmap_payload = {'target_addr': ipv4_addrs[0],
                               'target_port': https_port,
                               'target_name': name,
                               'target_component' : vm_type}
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)
            portmap_payload['target_port'] = 22
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect dd --name {}' to configure your new Data Domain server.".format(name))
        typewriter("Initial/default credentials are 'sysadmin' and 'changeme'")
