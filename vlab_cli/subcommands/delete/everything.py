# -*- coding: UTF-8 -*-
"""Defines the CLI for deleting everything a user owns in vLab"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task, block_on_tasks


@click.command()
@click.pass_context
def everything(ctx):
    """Destroy everything you own."""
    click.confirm(" Are you sure you want to destroy your entire lab?", abort=True)
    click.confirm(" Really sure? You cannot undo this, just like you cannot un-bake a cake.", abort=True)
    consume_task(vlab_api,
                 endpoint='/api/1/inf/power',
                 body={'machine': 'all', 'power': 'off'},
                 message='Powering down your lab',
                 timeout=300,
                 pause=5)
    consume_task(vlab_api,
                 endpoint='/api/1/inf/inventory',
                 message='Destroying inventory',
                 method='DELETE')
    resp = consume_task(vlab_api,
                        endpoint='/api/2/inf/vlan',
                        message='Determining what networks you own',
                        method='GET')
    vlans = resp.json()['content']
    tasks = {}
    with Spinner('Deleting networks'):
        for vlan in vlans.keys():
            resp = vlab_api.delete('/api/2/inf/vlan', json={'vlan-name': vlan})
            tasks[vlan] = resp.links['status']['url']
        block_on_tasks(vlab_api, tasks, pause=1)
