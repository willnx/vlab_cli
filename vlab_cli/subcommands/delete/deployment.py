# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a Deployment"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Deployment in your lab')
@click.pass_context
def deployment(ctx, name):
    """Delete a Deployment from your lab"""
    body = {'template': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/deployment',
                 message='Destroying Deployment {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
