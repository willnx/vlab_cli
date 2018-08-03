# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a jump box"""
import click

from vlab_cli.lib.api import consume_task


@click.command()
@click.pass_context
def jumpbox(ctx):
    """Destroy your jumpbox"""
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/1/inf/jumpbox',
                 message='Deleting your jump box',
                 method='DELETE')
    click.echo('OK!')
