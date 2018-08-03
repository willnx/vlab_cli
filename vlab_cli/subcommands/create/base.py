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
