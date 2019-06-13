# *-* coding: UTF-8 -*-
"""Define the CLI for taking a snapshot of a VM"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.converters import epoch_to_date
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM that owns the supplied snapshot')
@click.option('-s', '--shift', is_flag=True,
              help='Automatically create a new snapshot, and delete the oldest when a VM already has the maxinum number of snapshots')
@click.pass_context
def snapshot(ctx, name, shift):
    """Take a snapshot of a supplied VM"""
    body = {"name": name, "shift": shift}
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/snapshot',
                        message='Taking a snapshot of {}'.format(name),
                        body=body,
                        timeout=900,
                        pause=5).json()['content']
    typewriter('Successfully created a new snapshot of {}!'.format(name))
    rows = []
    rows.append(['Component Name', ':', name])
    rows.append(['Snapshot ID', ':', info[name][0]['id']])
    rows.append(['Expiration Date', ':', epoch_to_date(info[name][0]['expires'])])
    click.echo('\n{}\n'.format(tabulate(rows, tablefmt='plain')))
