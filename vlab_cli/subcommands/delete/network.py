# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying networks"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the network to destory')
@click.pass_context
def network(ctx, name):
    """Destroy a vLAN network"""
    if name in ('frontend', 'backend'):
        click.secho('WARNING: Deleting this network can render your lab unusable', bold=True)
        click.confirm('Are you sure you wish to continue?', abort=True)
    body = {'vlan-name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/2/inf/vlan',
                 message='Destroying network: {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
