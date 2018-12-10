# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Microsoft Server instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='2012R2', show_default=True, 
              help='The version of Microsoft Server to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Microsoft Server in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new Microsoft Server to')
@click.pass_context
def winserver(ctx, name, image, external_network):
    """Create a new Microsoft Server instance"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image.upper()} # upper in case they supply 2012r2
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/winserver',
                        message='Creating new instance of Microsoft Server {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
