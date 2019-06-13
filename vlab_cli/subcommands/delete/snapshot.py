# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a snapshot"""
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
def snapshot(ctx, name, snap_id):
    """Destory a snapshot of a supplied VM"""
    body = {"name": name, "id": snap_id}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/snapshot',
                        message='Destorying snapshot {} on VM {}'.format(snap_id, name),
                        body=body,
                        method='DELETE',
                        timeout=900,
                        pause=5)
    typewriter('OK!')
