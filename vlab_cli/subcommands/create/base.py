# -*- coding: UTF-8 -*-
"""The base grouping of the ``create`` subcommand"""
import click
from vlab_cli.subcommands.create.onefs import onefs
from vlab_cli.subcommands.create.gateway import gateway
from vlab_cli.subcommands.create.iiq import iiq
from vlab_cli.subcommands.create.network import network
from vlab_cli.subcommands.create.jumpbox import jumpbox
from vlab_cli.subcommands.create.esrs import esrs
from vlab_cli.subcommands.create.cee import cee
from vlab_cli.subcommands.create.router import router
from vlab_cli.subcommands.create.windows import windows
from vlab_cli.subcommands.create.winserver import winserver
from vlab_cli.subcommands.create.centos import centos
from vlab_cli.subcommands.create.icap import icap


@click.group()
def create():
    """Create a new component in your virtual lab"""
    pass

create.add_command(onefs)
create.add_command(gateway)
create.add_command(iiq)
create.add_command(network)
create.add_command(jumpbox)
create.add_command(esrs)
create.add_command(cee)
create.add_command(router)
create.add_command(windows)
create.add_command(winserver)
create.add_command(centos)
create.add_command(icap)
