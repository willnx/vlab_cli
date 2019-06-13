# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a snapshot"""
import click
from tabulate import tabulate

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.converters import epoch_to_date


@click.command()
@click.pass_context
def snapshot(ctx):
    """Display information about the snapshots in your lab"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/snapshot',
                        message='Looking up snapshots in your lab',
                        method='GET').json()['content']
    snap_header = ['Component Name', 'Snapshot ID', 'Expiration Date']
    rows = []
    for vm_name, data in info.items():
        row = []
        snap_ids = []
        exp_dates = []
        for snap in data:
            snap_id = snap['id']
            exp_date = epoch_to_date(snap['expires'])
            snap_ids.append(snap_id)
            exp_dates.append(exp_date)
        all_snaps = '\n'.join(snap_ids)
        rows.append([vm_name,
                     format_snapinfo(snap_ids),
                     format_snapinfo(exp_dates, default_blank_as='N/A')])
    snap_table = tabulate(rows, headers=snap_header, tablefmt='presto')
    click.echo('\n{}\n'.format(snap_table))


def format_snapinfo(info, default_blank_as=None):
    """Makes the acsii table prettier

    :Returns: String

    :param info: The information to format
    :type info: List

    :param default_blank_as: If the specific data is blank/empty, replace it with
                             the supplied value as a string. Defaults 'None'
    :type default_blank_as: PyObject
    """
    data = '\n'.join(info)
    if not data:
        data = str(default_blank_as)
    return data
