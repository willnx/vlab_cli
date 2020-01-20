# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an InsightIQ instances"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import https_to_port, get_ipv4_addrs


@click.command()
@click.option('-i', '--image', default='4.1.3', show_default=True,
              help='The version of InsightIQ to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the InsightIQ instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new IIQ instance to')
@click.pass_context
def insightiq(ctx, name, image, external_network):
    """Create an instance of InsightIQ"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/insightiq',
                        message='Creating a new instance of InsightIQ running {}'.format(image),
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
                               'target_component' : 'InsightIQ'}
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)
            portmap_payload['target_port'] = 22
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect insightiq --protocol console --name {}' to setup a login password".format(name))
        typewriter("for your new InsightIQ instance.")
