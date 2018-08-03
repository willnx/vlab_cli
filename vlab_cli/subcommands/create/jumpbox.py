# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a jumpbox"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import format_machine_info

@click.command()
@click.option('-n', '--network', default='frontend',
              help='The network to connect your jumpbox to')
@click.pass_context
def jumpbox(ctx, network):
    """Create a jumpbox for accessing your lab"""
    # prefixed username to network ensures unique network name
    body = {'network': '{}_{}'.format(ctx.obj.username, network)}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/jumpbox',
                        message='Creating a new jump box',
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
