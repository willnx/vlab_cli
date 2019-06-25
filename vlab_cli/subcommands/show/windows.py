# -*- coding: UTF-8 -*-
"""Defines the CLI for displaing information about Windows Desktop clients"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version

@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of Windows Desktop to deploy')
@click.pass_context
def windows(ctx, images):
    """Display information about the Windows Desktop clients in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/windows/image',
                            base_endpoint=False,
                            message='Collecting available versions of Windows Desktop',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(to_number(img))
        table = get_formatted_table(sorted(rows, reverse=True))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/windows',
                            message='Collecting information about your Windows clients',
                            method='GET').json()['content']
        output = vm_table_view(ctx.obj.vlab_api, info)
        if not output:
            output = 'You do not own any Windows Desktop clients'
        click.echo(output)


def to_number(value):
    """Cast a given string to a float or integer

    :Returns: Integer or Float

    :Raises: ValueError

    :param value: The string to cast to an integer
    :type value: String
    """
    try:
        as_number = int(value)
    except ValueError:
        as_number = float(value)
    return as_number


def get_formatted_table(images):
    """A human friendly table of the different Windows Desktop clients versions
    that are available for deployment.

    :Returns: String

    :param images: The available versions/images of Windows, ordered by version number
    :type images: List
    """
    header = ['Windows Desktop Clients']
    table = columned_table(header, [images])
    return table
