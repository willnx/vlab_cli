# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a Deployment in a user's lab"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-i', '--image', cls=MandatoryOption,
              help='The name of the template to deploy.')
@click.pass_context
def deployment(ctx, image):
    """Deploy a template of machines in your lab"""
    body = {'template' : image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/deployment',
                        message='Deploying template {}'.format(image),
                        body=body,
                        timeout=3600,
                        pause=20)
    data = resp.json()['content']
    typewriter("Successfully created the following machines:")
    click.echo('\t{}'.format('\n\t'.join(data.keys())))
    typewriter("\nUse 'vlab connect deployment --name <name> --protocol <protocol>' to access a deployed machine")
