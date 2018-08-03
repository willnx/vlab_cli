# -*- coding: UTF-8 -*-
"""Defines the CLI for viewing a details about a Jumpbox"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.pass_context
def jumpbox(ctx):
    """View details about your jump box"""
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/jumpbox',
                        message='Collecting information about your jump box',
                        method='GET')
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
