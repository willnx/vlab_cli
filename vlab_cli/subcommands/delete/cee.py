# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying an instance of EMC Common Event Enabler"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CEE instance in your lab')
@click.pass_context
def cee(ctx, name):
    """Delete an instance of EMC Common Event Enabler"""
    body = {'name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/cee',
                 message='Destroying CEE instance named {}'.format(name),
                 body=body,
                 method='DELETE')
    with Spinner('Deleting port mapping rules'):
        all_ports = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name': name}).json()['content']['ports']
        for port in all_ports.keys():
            ctx.obj.vlab_api.delete('/api/1/ipam/portmap', json={'conn_port': int(port)})
    click.echo('OK!')
