# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about Microsoft Servers"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table

@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of Microsoft Server to deploy')
@click.pass_context
def winserver(ctx, images):
    """Display information about the Microsoft Server instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/winserver/image',
                            base_endpoint=False,
                            message='Collecting available versions of Microsoft Server',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        table = get_formatted_table(sorted(rows, reverse=True))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/winserver',
                            message='Collecting information about your Microsoft Server instances',
                            method='GET').json()['content']
        output = vm_table_view(ctx.obj.vlab_api, info)
        if not output:
            output = 'You do not own any Windows Server instances'
        click.echo(output)


def get_formatted_table(images):
    """A human friendly table of the different Windows Desktop clients versions
    that are available for deployment.

    :Returns: String

    :param images: The available versions/images of Microsoft Server, ordered by version number
    :type images: List
    """
    header = ['Microsoft Server']
    table = columned_table(header, [images])
    return table
