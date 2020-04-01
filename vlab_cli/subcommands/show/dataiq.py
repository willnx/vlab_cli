# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about DataIQ instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of DataIQ to deploy')
@click.pass_context
def dataiq(ctx, images):
    """Display information about DataIQ instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/dataiq/image',
                            base_endpoint=False,
                            message='Collecting available versions of DataIQ for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(Version(img, name='DataIQ'))
        output = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(output))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/dataiq',
                            message='Collecting information about your DataIQ instances',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = 'You do not own any DataIQ instances'
        click.echo(output)

def get_formatted_table(images):
    """A human handy table of the different variants of DataIQ, and versions
    that can be deployed.

    :Returns: String

    :param images: The available version/images of DataIQ, ordered by version number
    :type images: List
    """
    header = ['1.0 (Mauna Kea)']
    table = columned_table(header, [images])
    return table
