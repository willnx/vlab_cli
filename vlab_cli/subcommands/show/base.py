# -*- coding: UTF-8 -*-
"""The base grouping of the ``show`` subcommand"""
import click

from vlab_cli.subcommands.show.onefs import onefs
from vlab_cli.subcommands.show.gateway import gateway
from vlab_cli.subcommands.show.iiq import insightiq
from vlab_cli.subcommands.show.network import network
from vlab_cli.subcommands.show.esrs import esrs
from vlab_cli.subcommands.show.cee import cee
from vlab_cli.subcommands.show.router import router
from vlab_cli.subcommands.show.windows import windows
from vlab_cli.subcommands.show.winserver import winserver
from vlab_cli.subcommands.show.centos import centos
from vlab_cli.subcommands.show.icap import icap
from vlab_cli.subcommands.show.claritynow import claritynow
from vlab_cli.subcommands.show.ecs import ecs
from vlab_cli.subcommands.show.portmap import portmap
from vlab_cli.subcommands.show.snapshot import snapshot
from vlab_cli.subcommands.show.esxi import esxi
from vlab_cli.subcommands.show.dataiq import dataiq
from vlab_cli.subcommands.show.dns import dns
from vlab_cli.subcommands.show.deployment import deployment
from vlab_cli.subcommands.show.template import template
from vlab_cli.subcommands.show.avamar import avamar
from vlab_cli.subcommands.show.ana import ana
from vlab_cli.subcommands.show.dd import dd


@click.group()
def show():
    """Display information about a specific component in your lab"""
    pass

show.add_command(onefs)
show.add_command(gateway)
show.add_command(insightiq)
show.add_command(network)
show.add_command(esrs)
show.add_command(cee)
show.add_command(router)
show.add_command(windows)
show.add_command(winserver)
show.add_command(centos)
show.add_command(icap)
show.add_command(claritynow)
show.add_command(ecs)
show.add_command(portmap)
show.add_command(snapshot)
show.add_command(esxi)
show.add_command(dataiq)
show.add_command(dns)
show.add_command(deployment)
show.add_command(template)
show.add_command(avamar)
show.add_command(ana)
show.add_command(dd)
