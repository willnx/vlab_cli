# -*- coding: UTF-8 -*-
"""Defines the CLI for deleting the displaying gateway"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task


@click.command()
@click.pass_context
def gateway(ctx):
    """Display information about network lab gateway"""
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/gateway',
                        message='Looking up your default gateway',
                        method='GET')
    info = resp.json()['content']
    shorter_link = ctx.obj.vlab_api.post('/api/1/link',
                                         json={'url': info['console']}).json()['content']['url']
    ip = [x for x in info['ips'] if not x.startswith('192.168.')]
    if ip:
        admin_url = 'https://{}:444'.format(ip[0])
    else:
        admin_url = None
    rows = []
    kind, version = info['note'].split('=')
    rows.append(['Type', ':', kind])
    rows.append(['Version', ':', version])
    rows.append(['State', ':', info['state']])
    rows.append(['Admin Page', ':', admin_url])
    rows.append(['Console', ':', shorter_link])
    click.echo(tabulate(rows, tablefmt='plain'))
