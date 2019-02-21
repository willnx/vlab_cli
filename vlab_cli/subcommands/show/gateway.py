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
    ip = [x for x in info['ips'] if not x.startswith('192.168.') and not ':' in x]
    if ip:
        gateway_ip = ','.join(ip)
    else:
        gateway_ip = 'None'
    rows = []
    kind = info['meta']['component']
    version = info['meta']['version']
    rows.append(['IP', ':', gateway_ip])
    rows.append(['State', ':', info['state']])
    rows.append(['Version', ':', version])
    rows.append(['Type', ':', kind])
    click.echo(tabulate(rows, tablefmt='plain'))
