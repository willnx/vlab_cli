# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Windows Desktop client"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', cls=MandatoryOption,
              help='The version of Windows to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the Windows client in your lab')
@click.option('-e', '--external-network', default='frontend',
              help='The public network to connect the new Windows client to')
@click.pass_context
def windows(ctx, name, image, external_network):
    """Create a new Windows Desktop client"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/windows',
                        message='Creating new instance of Windows {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
