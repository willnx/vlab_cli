# -*- coding: UTF-8 -*-
"""Defines the CLI for creating the Default gateway"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task


@click.command()
@click.option('-w', '--wan', default='corpNetwork', help='The name of the public network')
@click.option('-l', '--lan', default='frontend', help='The name of the private network')
@click.pass_context
def gateway(ctx, wan, lan):
    """Create a network gateway to your virtual lab"""
    # Network names must be unique. Prefixing the username is a simply hack
    click.secho('**NOTE**: Gateways can take 10-15 minutes to be created', bold=True)
    body = {'wan': wan, 'lan': '{}'.format(lan)}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/gateway',
                        message='Creating a new default gateway',
                        body=body,
                        timeout=900,
                        pause=5)
    info = resp.json()['content']
    shorter_link = ctx.obj.vlab_api.post('/api/1/link',
                                         json={'url': info['console']}).json()['content']['url']
    ip = [x for x in info['ips'] if not x.startswith('192.168.')]
    if ip:
        admin_url = 'https://{}:444'.format(ip[0])
    else:
        admin_url = None
    rows = []
    kind = info['meta']['component']
    version = info['meta']['version']
    rows.append(['Type', ':', kind])
    rows.append(['Version', ':', version])
    rows.append(['State', ':', info['state']])
    rows.append(['Admin Page', ':', admin_url])
    rows.append(['Console', ':', shorter_link])
    click.echo(tabulate(rows, tablefmt='plain'))
