# -*- coding: UTF-8 -*-
"""
Defines the CLI so users (if needed) can manually create port mapping/forwarding
rules.
"""
import click

from vlab_cli.subcommands.portmap.cee import cee
from vlab_cli.subcommands.portmap.centos import centos
from vlab_cli.subcommands.portmap.claritynow import claritynow
from vlab_cli.subcommands.portmap.ecs import ecs
from vlab_cli.subcommands.portmap.esrs import esrs
from vlab_cli.subcommands.portmap.icap import icap
from vlab_cli.subcommands.portmap.iiq import iiq
from vlab_cli.subcommands.portmap.onefs import onefs
from vlab_cli.subcommands.portmap.router import router
from vlab_cli.subcommands.portmap.windows import windows
from vlab_cli.subcommands.portmap.winserver import winserver


@click.group()
@click.pass_context
def portmap(ctx):
    """Manually create a port mapping/forwarding rule"""
    pass


portmap.add_command(cee)
portmap.add_command(centos)
portmap.add_command(claritynow)
portmap.add_command(ecs)
portmap.add_command(icap)
portmap.add_command(iiq)
portmap.add_command(onefs)
portmap.add_command(router)
portmap.add_command(windows)
portmap.add_command(winserver)
