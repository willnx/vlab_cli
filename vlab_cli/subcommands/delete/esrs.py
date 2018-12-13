# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying an instance of ESRS"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ESRS instance in your lab')
@click.pass_context
def esrs(ctx, name):
    """Delete an instance of ESRS"""
    body = {'name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/1/inf/esrs',
                 message='Destroying ESRS instance named {}'.format(name),
                 body=body,
                 method='DELETE')
    with Spinner('Deleting port mapping rules'):
        ctx.obj.vlab_api.delete_all_ports(name)
    click.echo('OK!')
