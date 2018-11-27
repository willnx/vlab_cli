# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to a OneFS node"""
import click

from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'scp', 'https']),
              default='ssh', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the node to connect to')
@click.pass_context
def onefs(ctx):
    """Connect to a OneFS node"""
    click.echo('woot')
