# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a CentOS instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', cls=MandatoryOption,
              help='The version of CentOS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CentOS instance in your lab')
@click.option('-e', '--external-network', default='frontend',
              help='The public network to connect the new CentOS instance to')
@click.pass_context
def centos(ctx, name, image, external_network):
    """Create an instance of CentOS"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/centos',
                        message='Creating new instance of CentOS {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
