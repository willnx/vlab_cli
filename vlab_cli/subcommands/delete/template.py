# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a deployment template"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the deployment template to delete.')
@click.pass_context
def template(ctx, name):
    """Delete a deployment template."""
    body = {'template': name}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/template',
                        base_endpoint=False,
                        body=body,
                        message='Destroying template {}'.format(name),
                        method='DELETE')
    data = resp.json()
    if data['error']:
        raise click.Exception(data['error'])
    else:
        click.echo("OK!")
