# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying an ICAP server"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ICAP server in your lab')
@click.pass_context
def icap(ctx, name):
    """Delete an ICAP Antivirus server"""
    body = {'name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/icap',
                 message='Destroying ICAP server named {}'.format(name),
                 body=body,
                 method='DELETE')
    with Spinner('Deleting port mapping rules'):
        all_ports = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name': name}).json()['content']['ports']
        for port in all_ports.keys():
            ctx.obj.vlab_api.delete('/api/1/ipam/portmap', json={'conn_port': int(port)})
    click.echo('OK!')
