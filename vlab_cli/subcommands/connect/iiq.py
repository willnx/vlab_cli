# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an InsightIQ instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'scp', 'https']),
              default='https', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the InsightIQ instance to connect to')
@click.pass_context
def insightiq(ctx, name, protocol):
    """Connect to an InsightIQ instance"""
    target_port = get_protocol_port('insightiq', protocol)
    with Spinner('Lookin up connection information for {}'.format(name)):
        resp = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name' : name, 'target_port' : target_port})
        try:
            conn_port = list(resp.json()['content'].keys())[0]
        except Exception as doh:
            ctx.obj.log.debug(doh, exc_info=True)
            conn_port = None
    if not conn_port:
        error = 'No mapping rule for {} to {} exists'.format(protocol, name)
        raise click.ClickException(error)

    conn = Connectorizer(ctx.obj.vlab_config, ctx.obj.vlab_api)
    if protocol == 'ssh':
        conn.ssh(port=conn_port)
    elif protocol == 'https':
        conn.https(port=conn_port)
    elif protocol == 'scp':
        conn.scp(port=conn_port)
    else:
        error = 'Unexpected protocol requested: {}'.format(protocol)
        raise RuntimeError(error)
