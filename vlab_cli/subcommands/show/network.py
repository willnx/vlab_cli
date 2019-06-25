# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying networks a user owns"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task


@click.command()
@click.option('-n', '--name', help='Show only this specific network')
@click.pass_context
def network(ctx, name):
    """Display the network(s) you own"""
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/vlan',
                        message='Collecting your networks',
                        method='GET')
    user_tag = "{}_".format(ctx.obj.username)
    networks = [x for x in resp.json()['content'].keys()]
    if name:
        networks = [x for x in networks if x == name]
    if networks:
        click.echo('\n{}\n'.format(tabulate([['\n'.join(networks)]], headers=['Name']), tablefmt='presto'))
    elif name:
        click.echo('No network with name: {}'.format(name))
    else:
        click.echo('No networks found')
