# -*- coding: UTF-8 -*-
"""Defines the CLI for creating OneFS nodes"""
from collections import OrderedDict

import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import block_on_tasks
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import vm_table_view


@click.command()
@click.option('-i', '--image', cls=MandatoryOption,
              help='The version of OneFS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the vOneFS node in your lab')
@click.option('-c', '--node-count', default=1, type=int,
              help='The number of nodes to create')
@click.option('-e', '--external', default='frontend',
              help='The public/external network to connect the node to')
@click.option('-t', '--internal', default='backend',
              help='The private/backend network to connect the node to')
@click.pass_context
def onefs(ctx, name, image, node_count, external, internal):
    """Create a vOneFS node"""
    if node_count > 5:
        raise click.ClickException('You can only deploy a maximum of 5 nodes at a time')
    tasks = {}
    with Spinner('Deploying {} nodes running {}'.format(node_count, image)):
        for idx in range(node_count):
            node_name = '{}-{}'.format(name, idx +1) # +1 so we don't have node-0
            body = {'name' : node_name,
                    'image': image,
                    'frontend': '{}_{}'.format(ctx.obj.username, external),
                    'backend': '{}_{}'.format(ctx.obj.username, internal)}
            resp = ctx.obj.vlab_api.post('/api/1/inf/onefs', json=body)
            tasks[node_name] = '/api/1/inf/onefs/task/{}'.format(resp.json()['content']['task-id'])
        info = block_on_tasks(ctx.obj.vlab_api, tasks)

    # Order the output by node; reduces instances of making node-5 really node 1
    # because humans tend to configure the nodes from top to bottom in the grid output
    ordered_nodes = OrderedDict()
    node_names = info.keys()
    ordered_names = sorted(node_names, key=node_sorter)
    for node_name in ordered_names:
        ordered_nodes[node_name] = info[node_name]['content'][node_name]
    table = vm_table_view(ctx.obj.vlab_api, ordered_nodes)
    click.echo('\n{}\n'.format(table))


def node_sorter(node_name):
    """A function to sort nodes vis-a-vis name"""
    return int(node_name.split('-')[-1])
