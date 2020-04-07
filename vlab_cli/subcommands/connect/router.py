# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an InsightIQ instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['console'], case_sensitive=False),
              default='console', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the network Router to connect to')
@click.pass_context
def router(ctx, name, protocol):
    """Connect to the console of a network router"""
    # Router only supports console access
    if protocol == 'console':
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/router',
                            message='Looking up connection info for {}'.format(name),
                            method='GET').json()
        if not info['content'].get(name, None):
            error = 'No Router named {} found'.format(name)
            raise click.ClickException(error)
        else:
            vm_moid = info['content'][name].get('moid', 'n/a')
        conn = Connectorizer(ctx.obj.vlab_config, gateway_ip='n/a')
        conn.console(vm_moid)
    else:
        error = 'Unexpected connection protocol supplied'
        raise click.ClickException(error)
