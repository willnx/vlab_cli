# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an InsightIQ instance"""
import getpass

import click

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
@click.option('-u', '--user', default='administrator',
              help='The name of the user to connect to the network Router as.')
@click.option('--password', default=False, is_flag=True,
              help='If supported, auto-enter the password when connecting.')
@click.pass_context
def router(ctx, name, protocol, user, password):
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
            if password:
                password_value = getpass.getpass('Password for {}: '.format(user))
                conn = Connectorizer(ctx.obj.vlab_config, info['content']['gateway_ip'], user=user, password=password_value)
            else:
                conn = Connectorizer(ctx.obj.vlab_config, info['content']['gateway_ip'], user=user)
        conn.console(vm_moid)
    else:
        error = 'Unexpected connection protocol supplied'
        raise click.ClickException(error)
