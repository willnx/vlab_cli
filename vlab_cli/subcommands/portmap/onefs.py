# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a port mapping rule to a OneFS node"""
import ipaddress

import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.click_extras import MandatoryOption, get_portmap_ip


@click.command()
@click.option('-a', '--ip-address', cls=MandatoryOption,
              help='Explicitly supply the IP of the OneFS node')
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'https']),
              default='https', show_default=True,
              help='The protocol to create a mapping rule for')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the OneFS node to create a rule for')
@click.pass_context
def onefs(ctx, name, protocol, ip_address):
    """Create a port mapping rule to an OneFS node instance"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/onefs',
                        message='Collecting information about your OneFS nodes',
                        method='GET').json()
    if not info['content']:
        if info['error']:
            ctx.log.debug('Error in server API response')
            error = info['error']
        else:
            error = 'No OneFS node named {} found'.format(name)
        raise click.ClickException(error)

    try:
        ipaddress.ip_address(ip_address)
    except ValueError as doh:
        raise click.ClickException(doh)
    else:
        ip = ip_address

    if protocol == 'https':
        port_number = 8080
    else:
        port_number = 22
    with Spinner("Mapping port"):
        try:
            ctx.obj.vlab_api.map_port(target_addr=ip,
                                      target_port=port_number,
                                      target_name=name,
                                      target_component=info['content'][name]['meta']['component'])
        except Exception as doh:
            ctx.obj.log.debug(doh, exc_info=True)
            raise click.Exception(doh)
    typewriter('OK!')
