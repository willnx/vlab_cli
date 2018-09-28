# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a Windows Desktop client"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Windows Desktop client in your lab')
@click.pass_context
def windows(ctx, name):
    """Delete a Windows Desktop client"""
    body = {'name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/1/inf/windows',
                 message='Destroying Windows Desktop client named {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
