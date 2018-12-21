# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an ECS instances"""
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
              help='The name of the ECS instance to connect to')
@click.pass_context
def ecs(ctx, name, protocol):
    """Connect to an ECS instances"""
    target_port = get_protocol_port('ecs', protocol)
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
    if protocol == 'ssh':
        conn.ssh(ip_addr=ctx.obj.vlab_api._ipam_ip, port=conn_port)
    elif protocol == 'https':
        conn.https(ip_addr=ctx.obj.vlab_api._ipam_ip, port=conn_port)
    elif protocol == 'scp':
        conn.scp(ip_addr=ctx.obj.vlab_api._ipam_ip, port=conn_port)
    else:
        error = 'Unexpected protocol requested: {}'.format(protocol)
        raise RuntimeError(error)
