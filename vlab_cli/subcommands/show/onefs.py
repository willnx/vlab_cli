# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about OneFS nodes"""
from collections import OrderedDict

import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table
from vlab_cli.lib.versions import Version

@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of OneFS to deploy')
@click.pass_context
def onefs(ctx, images):
    """Display information about vOneFS nodes in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/1/inf/onefs/image',
                            base_endpoint=False,
                            message='Collecting available versions of OneFS for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(Version(img, name='OneFS'))
        click.echo('\n{}\n'.format(rows))
        table = get_formatted_table(sorted(rows))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/1/inf/onefs',
                            message='Collecting information about your OneFS nodes',
                            method='GET').json()
        ordered_nodes = sort_node_list(info['content'])
        click.echo(vm_table_view(ctx.obj.vlab_api, ordered_nodes))


def get_formatted_table(images):
    """Return a human friendly table of different OneFS deployment options

    :Returns: String

    :param images: The different images available, sorted by version number
    :type images: List
    """
    header = ['8.0.0 (Riptide)',
              '8.0.1 (Halfpipe)',
              '8.1.0 (FreightTrain)',
              '8.1.1 (Niijima)',
              '8.1.2 (Kanagawa)',
             ]
    riptide = sorted([x for x in images if '7.2' < x < '8.0.1'])
    halfpipe = sorted([x for x in images if '8.0.0' < x < '8.1.0'])
    freight_train = sorted([x for x in images if '8.0.1'< x < '8.1.1'])
    niijima = sorted([x for x in images if '8.1.0' < x < '8.1.2'])
    kanagawa = sorted([x for x in images if '8.1.1' < x < '8.2.0'])
    table = columned_table(header, [riptide, halfpipe, freight_train, niijima, kanagawa])
    return table


def sort_node_list(the_nodes):
    """Order node by name, then by node number

    :Returns: collections.OrderedDict

    :param the_nodes: The mapping of node names to general info
    :type the_nodes: Dictionary
    """
    node_names = set([x.split('-')[0] for x in the_nodes.keys()])
    ordered_by_name = OrderedDict()
    for node in node_names:
        ordered_nodes = sorted([x for x in the_nodes if x.split('-')[0] == node],
                               key=node_sorter)
        for each_node in ordered_nodes:
            ordered_by_name[each_node] = the_nodes[each_node]
    return ordered_by_name


def node_sorter(node_name):
    """A function to sort nodes vis-a-vis name"""
    return int(node_name.split('-')[-1])
