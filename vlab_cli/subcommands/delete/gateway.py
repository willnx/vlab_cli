# -*- coding: UTF-8 -*-
"""Defines the CLI for deleting the Default gateway"""
import click

from vlab_cli.lib.api import consume_task


@click.command()
@click.pass_context
def gateway(ctx):
    """Delete your network gateway"""
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/gateway',
                 message='Deleting your gateway',
                 method='DELETE')
    click.echo('OK!')
