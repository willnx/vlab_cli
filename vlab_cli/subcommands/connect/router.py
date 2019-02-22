# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an InsightIQ instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['https']),
              default='https', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the network Router to connect to')
@click.pass_context
def router(ctx, name, protocol):
    """Connect to the HTTPS console of a network router"""
    # Router only supports console access
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/router',
                        message='Lookin up connection information for {}'.format(name),
                        method='GET').json()['content']
    vm = info.get(name, None)
    if not vm:
        error = 'You have no router named {}'.format(name)
        raise click.ClickException(error)
    conn = Connectorizer(ctx.obj.vlab_config, 'router-does-not-use-gateway')
    url = vm['console']
    conn.https(port=None, url=url)
