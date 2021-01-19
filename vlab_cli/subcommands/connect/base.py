# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting users to components in their lab"""
import click

from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.configurizer import CONFIG_SECTIONS, set_config, get_config
from vlab_cli.lib.clippy.connect import invoke_bad_missing_config, invoke_config

from vlab_cli.subcommands.connect.onefs import onefs
from vlab_cli.subcommands.connect.iiq import insightiq
from vlab_cli.subcommands.connect.esrs import esrs
from vlab_cli.subcommands.connect.cee import cee
from vlab_cli.subcommands.connect.router import router
from vlab_cli.subcommands.connect.windows import windows
from vlab_cli.subcommands.connect.winserver import winserver
from vlab_cli.subcommands.connect.centos import centos
from vlab_cli.subcommands.connect.icap import icap
from vlab_cli.subcommands.connect.claritynow import claritynow
from vlab_cli.subcommands.connect.ecs import ecs
from vlab_cli.subcommands.connect.esxi import esxi
from vlab_cli.subcommands.connect.dataiq import dataiq
from vlab_cli.subcommands.connect.dns import dns
from vlab_cli.subcommands.connect.deployment import deployment
from vlab_cli.subcommands.connect.avamar import avamar
from vlab_cli.subcommands.connect.ana import ana
from vlab_cli.subcommands.connect.dd import dd


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
                ctx.obj.vlab_config = get_config()
            except Exception as doh:
                ctx.obj.log.debug(doh, exc_info=True)
                raise click.ClickException(doh)


connect.add_command(onefs)
connect.add_command(insightiq)
connect.add_command(esrs)
connect.add_command(cee)
connect.add_command(router)
connect.add_command(windows)
connect.add_command(winserver)
connect.add_command(centos)
connect.add_command(icap)
connect.add_command(claritynow)
connect.add_command(ecs)
connect.add_command(esxi)
connect.add_command(dataiq)
connect.add_command(dns)
connect.add_command(deployment)
connect.add_command(avamar)
connect.add_command(ana)
connect.add_command(dd)
