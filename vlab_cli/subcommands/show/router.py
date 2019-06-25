# -*- coding: UTF-8 -*-
"""Defines the CLI for showing/displaying the network routers a user owns"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of network routers to deploy')
@click.pass_context
def router(ctx, images):
    """Display information about network routers in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/router/image',
                            base_endpoint=False,
                            message='Collecting available versions of network routers for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(Version(img, name='Router'))
        table = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/router',
                            message='Collecting information about the network routers in your lab',
                            method='GET').json()['content']
        output = vm_table_view(ctx.obj.vlab_api, info)
        if not output:
            output = 'You do not own any network Routers'
        click.echo(output)


def get_formatted_table(images):
    """A human handy table of the different versions of network routers that can
    be deployed.

    :Returns: String

    :param images: The available versions of network routers, ordered by version number
    :type images: List
    """
    header = ['VyOS Router']
    table = columned_table(header, [images])
    return table
