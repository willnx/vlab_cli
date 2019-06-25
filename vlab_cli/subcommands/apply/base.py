# -*- coding: UTF-8 -*-
"""Defines the CLI for applying changes to vLab"""
import click

from vlab_cli.subcommands.apply.snapshot import snapshot
from vlab_cli.subcommands.apply.network import network


@click.group()
@click.pass_context
def apply(ctx):
    """Apply a change to something"""
    pass


apply.add_command(snapshot)
apply.add_command(network)
