# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an Avamar server"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import get_protocol_port, get_component_protocols


@click.command()
@click.option('-i', '--image', default='19.4.0.116', show_default=True,
              help='The version of Avamar NDMP Accelerators to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Avamar NDMP Accelerators in your lab')
@click.option('-s', '--static-ip', cls=MandatoryOption,
              help='The static IP to assign your DNS server')
@click.option('-m', '--external-netmask', default='255.255.255.0', show_default=True,
              help='The subnet mask to use on the public network')
@click.option('-g', '--default-gateway', default='192.168.1.1', show_default=True,
              help='The default gateway to use on the public network')
@click.option('-d', '--dns-servers', default=['192.168.1.1'], multiple=True, show_default=True,
              help='The DNS server(s) to configure for the host OS')
@click.option('-o', '--domain', default='vlab.local', show_default=True,
              help='The domain part of an FQDN (i.e. everything except the hostname).')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new Microsoft Server to')
@click.pass_context
def ana(ctx, name, image, static_ip, external_netmask, default_gateway, dns_servers, domain, external_network):
    """Create a new Avamar NDMP accelerator."""
    body = {'network': external_network,
            'name': name,
            'image': image,
            'ip-config': {'static-ip': static_ip,
                          'default-gateway': default_gateway,
                          'netmask': external_netmask,
                          'dns': dns_servers,
                          'domain': domain
                         }
            }
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/avamar/ndmp-accelerator',
                        message='Creating a new Avamar NDMP accelerator running version {}'.format(image),
                        body=body,
                        timeout=1800,
                        pause=5)
    data = resp.json()['content'][name]
    vm_type = data['meta']['component']
    with Spinner('Creating port mapping rules for HTTPS and SSH'):
        protocols = get_component_protocols(vm_type.lower())
        for protocol in protocols:
            port = get_protocol_port(vm_type, protocol)
            payload = {'target_addr' : static_ip, 'target_port' : port,
                       'target_name' : name, 'target_component' : vm_type}
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=payload)


    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    msg = "Use 'vlab connect avamar --name {} --protocol mgmt' to setup your new Avamar Server\n".format(name)
    msg += "The default credentials are 'root' and 'changme'".format(name)
    typewriter(msg)
