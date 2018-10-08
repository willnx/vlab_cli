# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying an ICAP server"""
import click

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
                 endpoint='/api/1/inf/icap',
                 message='Destroying ICAP server named {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
