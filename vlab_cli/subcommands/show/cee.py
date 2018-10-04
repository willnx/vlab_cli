# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about EMC Common Event Enabler instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of CEE to deploy')
@click.pass_context
def cee(ctx, images):
    """Display information about EMC Common Event Enabler instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/1/inf/cee/image',
                            base_endpoint=False,
                            message='Collecting available versions of CEE for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(Version(img, name='CEE'))
        table = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/1/inf/cee',
                            message='Collecting information about your CEE instances',
                            method='GET').json()
        click.echo(vm_table_view(ctx.obj.vlab_api, info['content']))


def get_formatted_table(images):
    """A human handy table of the different variants of CEE, and versions
    that can be deployed.

    :Returns: String

    :param images: The available version/images of IIQ, ordered by version number
    :type images: List
    """
    header = ['CEE (Windows)']
    table = columned_table(header, [images])
    return table
