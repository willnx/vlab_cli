# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about DNS instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of DNS to deploy')
@click.pass_context
def dns(ctx, images):
    """Display information about DNS servers in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/dns/image',
                            base_endpoint=False,
                            message='Collecting available versions of DNS servers for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        output = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(output))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/dns',
                            message='Collecting information about your DNS servers',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = 'You do not own DNS servers'
        click.echo(output)


def get_formatted_table(images):
    """Obtain a human-friendly table of available DNS versions

    :Returns: String

    :param images: The available version/images of IIQ, ordered by version number
    :type images: List
    """
    header = ['DNS Servers']
    table = columned_table(header, [images])
    return table
