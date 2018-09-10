# -*- coding: UTF -*-
"""The grouping of the ``delete`` subcommand"""
import click

from vlab_cli.subcommands.delete.onefs import onefs
from vlab_cli.subcommands.delete.gateway import gateway
from vlab_cli.subcommands.delete.iiq import iiq
from vlab_cli.subcommands.delete.network import network
from vlab_cli.subcommands.delete.jumpbox import jumpbox
from vlab_cli.subcommands.delete.esrs import esrs
from vlab_cli.subcommands.delete.cee import cee
from vlab_cli.subcommands.delete.router import router

@click.group()
def delete():
    """Remove a component from your lab"""
    pass

delete.add_command(onefs)
delete.add_command(gateway)
delete.add_command(iiq)
delete.add_command(network)
delete.add_command(jumpbox)
delete.add_command(esrs)
delete.add_command(cee)
delete.add_command(router)
