# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about ECS instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of ECS to deploy')
@click.pass_context
def ecs(ctx, images):
    """Display information about Elastic Cloud Storage instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/ecs/image',
                            base_endpoint=False,
                            message='Collecting available versions of ECS for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        table = get_formatted_table(sorted(rows, reverse=True))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/ecs',
                            message='Collecting information about your ECS instances',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = 'You do not own any ECS instances'
        click.echo(output)


def get_formatted_table(images):
    """Obtain a human-friendly table of available ECS versions

    :Returns: String

    :param images: The available version/images of ECS, ordered by version number
    :type images: List
    """
    header = ['ECS']
    table = columned_table(header, [images])
    return table
