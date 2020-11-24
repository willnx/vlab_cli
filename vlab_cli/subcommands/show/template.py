# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about deployment templates."""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import deployment_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-v', '--verbose', is_flag=True,
              help='Display extra information about the templates.')
@click.pass_context
def template(ctx, verbose):
    """Display information about deployment templates you own/maintain."""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/deployment/image?verbose=true',
                        base_endpoint=False,
                        message='Collecting available Deployment templates',
                        method='GET').json()['content']
    
    if info['image']:
        click.echo('')
        for image in info['image']:
            for name, details in image.items():
                click.echo(deployment_table(name, details, verbose))
    else:
        click.echo("You do not own any deployment templates.")
