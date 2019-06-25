# -*- coding: UTF-8 -*-
"""Defines the CLI for creating vLan networks"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption, HiddenOption

@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the new network to make')
@click.option('--switch', cls=HiddenOption, default='vLabSwitch')
@click.pass_context
def network(ctx, name, switch):
    """Create a new vLAN network"""
    body = {'vlan-name': name, 'switch-name': switch}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/vlan',
                 message='Createing a new network named {}'.format(name),
                 body=body)
    click.echo('OK!')
