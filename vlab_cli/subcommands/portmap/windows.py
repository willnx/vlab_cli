# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a port mapping rule to a Windows Desktop instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.click_extras import MandatoryOption, get_portmap_ip


@click.command()
@click.option('-a', '--ip-address',
              help='Explicitly supply the IP of the Windows Desktop instance')
@click.option('-p', '--protocol', type=click.Choice(['rdp']),
              default='https', show_default=True,
              help='The protocol to create a mapping rule for')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Windows Desktop instance to create a rule for')
@click.pass_context
def windows(ctx, name, protocol):
    """Create a port mapping rule to a Windows Desktop instance"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/windows',
                        message='Collecting information about your Windows Desktop instances',
                        method='GET').json()
    if not info['content']:
        if info['error']:
            ctx.log.debug('Error in server API response')
            error = info['error']
        else:
            error = 'No Windows Desktop instance named {} found'.format(name)
        raise click.ClickException(error)

    ips = [x for x in info['content'][name]['ips'] if ":" not in x]
    ip = get_portmap_ip(ips, ip_address)
    port_number = 3389
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
