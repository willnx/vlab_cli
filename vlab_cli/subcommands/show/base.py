# -*- coding: UTF-8 -*-
"""The base grouping of the ``show`` subcommand"""
import click

from vlab_cli.subcommands.show.onefs import onefs
from vlab_cli.subcommands.show.gateway import gateway
from vlab_cli.subcommands.show.iiq import iiq
from vlab_cli.subcommands.show.network import network
from vlab_cli.subcommands.show.jumpbox import jumpbox
from vlab_cli.subcommands.show.esrs import esrs
from vlab_cli.subcommands.show.cee import cee
from vlab_cli.subcommands.show.router import router
from vlab_cli.subcommands.show.windows import windows
from vlab_cli.subcommands.show.winserver import winserver
from vlab_cli.subcommands.show.centos import centos
from vlab_cli.subcommands.show.icap import icap
from vlab_cli.subcommands.show.claritynow import claritynow


@click.group()
def show():
    """Display information about a specific component in your lab"""
    pass

show.add_command(onefs)
show.add_command(gateway)
show.add_command(iiq)
show.add_command(network)
show.add_command(jumpbox)
show.add_command(esrs)
show.add_command(cee)
show.add_command(router)
show.add_command(windows)
show.add_command(winserver)
show.add_command(centos)
show.add_command(icap)
show.add_command(claritynow)
