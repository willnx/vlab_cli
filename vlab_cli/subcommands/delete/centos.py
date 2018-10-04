# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying an instance of CentOS"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the CentOS instance in your lab')
@click.pass_context
def centos(ctx, name):
    """Delete an instance of CentOS"""
    body = {'name': name}
    consume_task(ctx.obj.vlab_api,
                 endpoint='/api/1/inf/centos',
                 message='Destroying CentOS instance named {}'.format(name),
                 body=body,
                 method='DELETE')
    click.echo('OK!')
