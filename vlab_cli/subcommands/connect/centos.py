# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to a CentOS instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['ssh']),
              default='ssh', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CentOS instance to connect to')
@click.pass_context
def centos(ctx, name, protocol):
    """Connect to a CentOS instance"""
    target_port = get_protocol_port('centos', protocol)
    with Spinner('Lookin up connection information for {}'.format(name)):
        conn_port = None
        ports = ctx.obj.vlab_api.get_port_map()
        for port, details in ports.items():
            if details['name'] == name and details['target_port'] == target_port:
                conn_port = port
    if not conn_port:
        error = 'No mapping rule for {} to {} exists'.format(protocol, name)
        raise click.ClickException(error)

    conn = Connectorizer(ctx.obj.vlab_config)
    conn.ssh(ip_addr=ctx.obj._ipam_ip, port=conn_port)