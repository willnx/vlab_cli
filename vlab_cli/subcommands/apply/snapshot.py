# -*- coding: UTF-8 -*-
"""Defines the CLI for reverting a VM to a snapshot"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-d', '--snap-id', cls=MandatoryOption,
              help='The snapshot ID to revert to')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM that owns the supplied snapshot')
@click.pass_context
def snapshot(ctx, snap_id, name):
    """Revert a VM to a given snapshot"""
    body = {"id": snap_id, "name": name}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/snapshot',
                        message='Reverting {} to snapshot {}'.format(name, snap_id),
                        body=body,
                        method='PUT',
                        timeout=900,
                        pause=5)
    typewriter('OK!')
