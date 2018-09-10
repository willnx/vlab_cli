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
