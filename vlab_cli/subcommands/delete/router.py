# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a network router"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the network router to destory')
@click.pass_context
def router(ctx, name):
    """Destroy a network router"""
    body = {'name': '{}'.format(name)}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/router',
                 message='Destroying network router: {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
