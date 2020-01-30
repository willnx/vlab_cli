# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about InsightIQ instances"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of InsightIQ to deploy')
@click.pass_context
def insightiq(ctx, images):
    """Display information about InsightIQ instances in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/insightiq/image',
                            base_endpoint=False,
                            message='Collecting available versions of InsightIQ for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(Version(img, name='InsightIQ'))
        table = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/insightiq',
                            message='Collecting information about your InsightIQ instances',
                            method='GET').json()
        output = vm_table_view(ctx.obj.vlab_api, info['content'])
        if not output:
            output = "You do not own any InsightIQ instances"
        click.echo(output)


def get_formatted_table(images):
    """A human handy table of the different branches of InsightIQ, and versions
    that can be deployed.

    :Returns: String

    :param images: The available version/images of IIQ, ordered by version number
    :type images: List
    """
    header = ['2.5 (Candle)',
              '3.0 (Lantern)',
              '3.1 (Beacon)',
              '3.2 (Lumen)',
              '4.0 (Aurora)',
              '4.1 (Sol)'
             ]
    candle  = [x for x in images if '2.5' < x < '3.0']
    lantern = [x for x in images if '3.0' < x < '3.1.0']
    beacon  = [x for x in images if '3.1' < x < '3.2.0']
    lumen   = [x for x in images if '3.2' < x < '4.0.0']
    aurora  = [x for x in images if '4.0' < x < '4.1.0']
    sol     = [x for x in images if '4.1' < x < '4.2.0']
    table = columned_table(header, [candle, lantern, beacon, lumen, aurora, sol])
    return table
