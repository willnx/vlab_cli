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
                 endpoint='/api/1/inf/cee',
                 message='Destroying CEE instance named {}'.format(name),
                 body=body,
                 method='DELETE')
    with Spinner('Deleting port mapping rules'):
        ctx.obj.vlab_api.delete_all_ports(name)
    click.echo('OK!')
