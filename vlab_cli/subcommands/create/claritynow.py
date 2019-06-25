# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a ClarityNow instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import https_to_port, get_ipv4_addrs


@click.command()
@click.option('-i', '--image', default='2.11.0', show_default=True,
              help='The version of ClarityNow to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ClarityNow instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new ClarityNow instance to')
@click.pass_context
def claritynow(ctx, name, image, external_network):
    """Create an instance of ClarityNow"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/claritynow',
                        message='Creating a new instance of ClarityNow {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    if ipv4_addrs:
        vm_type = data['meta']['component']
        https_port = https_to_port(vm_type.lower())
        with Spinner('Creating an SSH, RDP, and HTTPS port mapping rules'):
            for ipv4 in ipv4_addrs:
                portmap_payload = {'target_addr' : ipv4, 'target_port' : 22,
                                   'target_name' : name, 'target_component' : vm_type}
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

                portmap_payload['target_port'] = 3389
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

                portmap_payload['target_port'] = https_port
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    info = """\n    ***IMPORTANT***

    ClarityNow requires a valid license to operate.
    Your ClarityNow server license will expire in 60 days.
    """
    click.secho(info, bold=True)
    if ipv4_addrs:
        typewriter("Use 'vlab connect claritynow --name {}' to access your new ClarityNow instance".format(name))
