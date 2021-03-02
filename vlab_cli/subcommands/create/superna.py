# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Superna Eyeglass server"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-i', '--image', default='2.5.6', show_default=True,
              help='The version of Superna Eyeglass to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Superna Eyeglass server in your lab')
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
              help='The public network to connect the new Superna Eyeglass server to')
@click.pass_context
def superna(ctx, name, image, static_ip, external_netmask, default_gateway, dns_servers, domain, external_network):
    """Create a new Superna Eyeglass server."""
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
                        endpoint='/api/2/inf/superna',
                        message='Creating a new Superna Eyeglass server running version {}'.format(image),
                        body=body,
                        timeout=1800,
                        pause=5)
    data = resp.json()['content'][name]
    vm_type = data['meta']['component']
    with Spinner('Creating port a mapping rule for SSH.'):
        payload = {'target_addr' : static_ip, 'target_port' : 22,
                   'target_name' : name, 'target_component' : vm_type}
        ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    msg = "Use 'vlab connect avamar --name {} --protocol ssh' to setup your new Superna Eyeglass server\n".format(name)
    msg += "The default credentials are 'admin' and '3y3gl4ss'".format(name)
    typewriter(msg)
