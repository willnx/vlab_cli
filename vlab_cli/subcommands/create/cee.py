# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an EMC Common Event Enabler instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='8.5.1', show_default=True,
              help='The version of CEE to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CEE instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new CEE instance to')
@click.pass_context
def cee(ctx, name, image, external_network):
    """Create an instance of EMC Common Event Enabler"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/cee',
                        message='Creating new instance of CEE running {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
