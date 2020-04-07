# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an EMC Common Event Enabler instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['rdp', 'console'], case_sensitive=False),
              default='rdp', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CEE instance to connect to')
@click.pass_context
def cee(ctx, name, protocol):
    """Connect to a EMC Common Event Enabler instance"""
    if protocol == 'console':
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/cee',
                            message='Looking up connection info for {}'.format(name),
                            method='GET').json()
        if not info['content'].get(name, None):
            error = 'No CEE VM named {} found'.format(name)
            raise click.ClickException(error)
        else:
            vm_moid = info['content'][name].get('moid', 'n/a')
        conn = Connectorizer(ctx.obj.vlab_config, gateway_ip='n/a')
        conn.console(vm_moid)
    else:
        target_port = get_protocol_port('cee', protocol)
        with Spinner('Lookin up connection information for {}'.format(name)):

            resp = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name' : name, 'target_port' : target_port}).json()
            try:
                conn_port = list(resp['content']['ports'].keys())[0]
            except Exception as doh:
                ctx.obj.log.debug(doh, exc_info=True)
                conn_port = None
        if not conn_port:
            error = 'No mapping rule for {} to {} exists'.format(protocol, name)
            raise click.ClickException(error)
        conn = Connectorizer(ctx.obj.vlab_config, resp['content']['gateway_ip'])
        conn.rdp(port=conn_port)
