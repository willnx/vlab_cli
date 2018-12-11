# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a port mapping rule to EMC ESRS"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.click_extras import MandatoryOption, get_portmap_ip


@click.command()
@click.option('-a', '--ip-address',
              help='Explicitly supply the IP of the EMC ESRS instance')
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'https']),
              default='https', show_default=True,
              help='The protocol to create a mapping rule for')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the EMC ESRS instance to create a rule for')
@click.pass_context
def esrs(ctx, name, protocol):
    """Create a port mapping rule to an EMC ESRS instance"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/esrs',
                        message='Collecting information about your EMC ECS instances',
                        method='GET').json()
    if not info['content']:
        if info['error']:
            ctx.log.debug('Error in server API response')
            error = info['error']
        else:
            error = 'No EMC ECS instance named {} found'.format(name)
        raise click.ClickException(error)

    ips = [x for x in info['content'][name]['ips'] if ":" not in x]
    ip = get_portmap_ip(ips, ip_address)
    if protocol == 'https':
        port_number = 443
    else:
        port_number = 22
    with Spinner("Mapping port"):
        try:
            ctx.obj.vlab_api.map_port(target_addr=ips,
                                      target_port=port_number,
                                      target_name=name,
                                      target_component=info['content'][name]['meta']['component'])
        except Exception as doh:
            ctx.obj.log.debug(doh, exc_info=True)
            raise click.Exception(doh)
    typewriter('OK!')
