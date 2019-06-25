# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about ICAP servers"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of CentOS to deploy')
@click.pass_context
def icap(ctx, images):
    """Display information about ICAP Antivirus servers in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/icap/image',
                            base_endpoint=False,
                            message='Collecting available versions of ICAP servers for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        table = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/icap',
                            message='Collecting information about your ICAP servers',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = 'You do not own any ICAP servers'
        click.echo(output)


def get_formatted_table(images):
    """Obtain a human-friendly table of available CentOS versions

    :Returns: String

    :param images: The available version/images of IIQ, ordered by version number
    :type images: List
    """
    header = ['McAfee']
    table = columned_table(header, [images])
    return table
