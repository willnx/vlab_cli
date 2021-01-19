# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a DNS instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_component_protocols, network_config_ok, get_protocol_port
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='Windows2019', show_default=True,
              help='The version of DNS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the DNS instance in your lab')
@click.option('-s', '--static-ip', cls=MandatoryOption,
              help='The static IP to assign your DNS server')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new DNS server to')
@click.option('-m', '--external-netmask', default='255.255.255.0', show_default=True,
              help='The subnet mask to use on the public network')
@click.option('-g', '--default-gateway', default='192.168.1.1', show_default=True,
              help='The default gateway to use on the public network')
@click.option('-d', '--dns-servers', default=['192.168.1.1'], multiple=True, show_default=True,
              help='The DNS server(s) to configure for the host OS')
@click.pass_context
def dns(ctx, name, image, external_network, external_netmask, default_gateway,
           dns_servers, static_ip):
    """Create a DNS server"""
    error = network_config_ok(static_ip, default_gateway, external_netmask)
    if error:
        raise click.ClickException(error)
    body = {'network': external_network,
            'name': name,
            'image': image,
            'static-ip': static_ip,
            'default-gateway': default_gateway,
            'external-netmask': external_netmask,
            'dns-servers': dns_servers}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/dns',
                        message='Creating a new DNS server running {}'.format(image),
                        body=body,
                        timeout=1800,
                        pause=5)
    data = resp.json()['content'][name]
    data['ips'] = [static_ip]
    vm_type = data['meta']['component']
    if image.lower().startswith('windows'):
        protocols = ['rdp']
    else:
        protocols = ['ssh']
    with Spinner('Creating a port mapping rule for {}'.format(protocols[0].upper())):
        for protocol in protocols:
            target_port = get_protocol_port(vm_type.lower(), protocol)
            portmap_payload = {'target_addr' : static_ip, 'target_port' : target_port,
                               'target_name' : name, 'target_component' : vm_type}
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)

    typewriter("\nUse 'vlab connect dns --name {} --protocol {}' to access your new dns instance".format(name, protocols[0]))
