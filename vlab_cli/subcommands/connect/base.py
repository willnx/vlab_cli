# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting users to components in their lab"""
import click

from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.configurizer import CONFIG_SECTIONS, set_config
from vlab_cli.lib.clippy.connect import invoke_bad_missing_config, invoke_config

from vlab_cli.subcommands.connect.onefs import onefs

@click.group()
@click.pass_context
def connect(ctx):
    """Connect to a component in your lab"""
    bad_config = False
    if not ctx.obj.vlab_config:
        bad_config = True
        sections = {}
    else:
        sections = set(ctx.obj.vlab_config.sections())
    if CONFIG_SECTIONS != sections:
        bad_config = True

    if bad_config:
        fix_it = invoke_bad_missing_config(ctx.obj.username, ctx.obj.vlab_url)
        click.echo('') # because cramming text into a giant block is ugly
        if not fix_it:
            raise click.ClickException('Command "vlab connect" requires valid config file')
        else:
            try:
                new_config = invoke_config()
                set_config(new_config)
            except Exception as doh:
                ctx.obj.log.debug(doh, exc_info=True)
                raise click.ClickException(doh)


connect.add_command(onefs)