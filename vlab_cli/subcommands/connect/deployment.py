# -*- coding: UTF-8 -*-
"""Defines the CLI interface for connecting to machines of a deployment template"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', cls=MandatoryOption,
              type=click.Choice(['ssh', 'scp', 'console', 'rdp', 'https'], case_sensitive=False),
              help='The protocol to connect with.')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the machine to connect to')
@click.pass_context
def deployment(ctx, name, protocol):
    """Connect to a deployed machine"""
    if protocol == 'console':
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/deployment',
                            message='Looking up connection info for {}'.format(name),
                            method='GET').json()
        if not info['content'].get(name, None):
            error = 'No Deployment VM named {} found'.format(name)
            raise click.ClickException(error)
        else:
            vm_moid = info['content'][name].get('moid', 'n/a')
        conn = Connectorizer(ctx.obj.vlab_config, gateway_ip='n/a')
        conn.console(vm_moid)
    else:
        with Spinner('Looking up connection information for {}'.format(name)):
            data = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name' : name}).json()['content']
            ports = data['ports']
            port_map = {ports[x]['target_port']:x for x in ports.keys()}
            try:
                conn_port = determine_port(protocol, port_map)
            except Exception as doh:
                ctx.obj.log.debug(doh, exc_info=True)
                conn_port = None
        if not conn_port:
            error = 'No mapping rule for {} to {} exists'.format(protocol, name)
            raise click.ClickException(error)

        conn = Connectorizer(ctx.obj.vlab_config, data['gateway_ip'])
        if protocol == 'ssh':
            conn.ssh(port=conn_port)
        elif protocol == 'scp':
            conn.scp(port=conn_port)
        elif protocol == 'rdp':
            conn.rdp(port=conn_port)
        elif protocol == 'https':
            conn.https(port=conn_port)
        else:
            error = 'Unexpected protocol requested: {}'.format(protocol)
            raise RuntimeError(error)


def determine_port(protocol, port_map):
    if protocol == 'ssh' or protocol == 'scp':
        return port_map[22]
    elif protocol == 'rdp':
        return port_map[3389]
    else:
        # HTTPS is ran via different TCP ports for different components.
        # So, filter all the other possible ports out and whatever remains is HTTPS.
        # I'm doing it this way to avoid side effects (modifying the port_map dictionary).
        return [port_map[x] for x in port_map.keys() if x != 22 or x != 3389][0]
