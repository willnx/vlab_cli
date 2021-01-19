# -*- coding: UTF -*-
"""The grouping of the ``delete`` subcommand"""
import click

from vlab_cli.subcommands.delete.onefs import onefs
from vlab_cli.subcommands.delete.gateway import gateway
from vlab_cli.subcommands.delete.iiq import insightiq
from vlab_cli.subcommands.delete.network import network
from vlab_cli.subcommands.delete.esrs import esrs
from vlab_cli.subcommands.delete.cee import cee
from vlab_cli.subcommands.delete.router import router
from vlab_cli.subcommands.delete.windows import windows
from vlab_cli.subcommands.delete.winserver import winserver
from vlab_cli.subcommands.delete.centos import centos
from vlab_cli.subcommands.delete.icap import icap
from vlab_cli.subcommands.delete.claritynow import claritynow
from vlab_cli.subcommands.delete.ecs import ecs
from vlab_cli.subcommands.delete.portmap import portmap
from vlab_cli.subcommands.delete.snapshot import snapshot
from vlab_cli.subcommands.delete.esxi import esxi
from vlab_cli.subcommands.delete.dataiq import dataiq
from vlab_cli.subcommands.delete.dns import dns
from vlab_cli.subcommands.delete.deployment import deployment
from vlab_cli.subcommands.delete.template import template
from vlab_cli.subcommands.delete.avamar import avamar
from vlab_cli.subcommands.delete.ana import ana
from vlab_cli.subcommands.delete.dd import dd


@click.group()
def delete():
    """Remove a component from your lab"""
    pass

delete.add_command(onefs)
delete.add_command(gateway)
delete.add_command(insightiq)
delete.add_command(network)
delete.add_command(esrs)
delete.add_command(cee)
delete.add_command(router)
delete.add_command(windows)
delete.add_command(winserver)
delete.add_command(centos)
delete.add_command(icap)
delete.add_command(claritynow)
delete.add_command(ecs)
delete.add_command(portmap)
delete.add_command(snapshot)
delete.add_command(esxi)
delete.add_command(dataiq)
delete.add_command(dns)
delete.add_command(deployment)
delete.add_command(template)
delete.add_command(avamar)
delete.add_command(ana)
delete.add_command(dd)
