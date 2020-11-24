# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about a Deployment in a user's lab"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, deployment_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available templates to deploy.')
@click.option('-v', '--verbose', is_flag=True,
              help='Display extra information about the templates.')
@click.pass_context
def deployment(ctx, images, verbose):
    """Display information about a Deployment in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/deployment/image?verbose=true',
                            base_endpoint=False,
                            message='Collecting available Deployment templates',
                            method='GET').json()['content']
        click.echo('')
        for image in info['image']:
            for name, details in image.items():
                click.echo(deployment_table(name, details, verbose))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/deployment',
                            message='Collecting information about Deployments in your lab',
                            method='GET').json()
        if info['content']:
            click.echo(vm_table_view(ctx.obj.vlab_api, info['content']))
        else:
            click.echo("You do not have an active Deployment in your lab.")
