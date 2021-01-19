# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information Data Domain servers"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of Data Domain to deploy')
@click.pass_context
def dd(ctx, images):
    """Display information about Data Domain servers in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/data-domain/image',
                            base_endpoint=False,
                            message='Collecting available versions of Data Domain for deployment',
                            method='GET').json()['content']
        table = get_formatted_table(sorted(info['image'], reverse=True))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/data-domain',
                            message='Collecting information about your Data Domain servers',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = "You do not own any Data Domain servers."
        click.echo(output)


def get_formatted_table(images):
    """Obtain a human-friendly table of available Data Domain versions

    :Returns: String

    :param images: The available version/images of Data Domain, ordered by version number
    :type images: List
    """
    header = ['Data Domain']
    table = columned_table(header, [images])
    return table
