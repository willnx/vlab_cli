# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about ESXi instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of ESXi to deploy')
@click.pass_context
def esxi(ctx, images):
    """Display information about VMware ESXi instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/esxi/image',
                            base_endpoint=False,
                            message='Collecting available versions of ESXi for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        table = get_formatted_table(sorted(rows, reverse=True))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/esxi',
                            message='Collecting information about your ESXi instances',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = 'You do not own any ESXi instances'
        click.echo(output)


def get_formatted_table(images):
    """Obtain a human-friendly table of available ESXi versions

    :Returns: String

    :param images: The available version/images of ESXi, ordered by version number
    :type images: List
    """
    header = ['ESXi']
    table = columned_table(header, [images])
    return table
