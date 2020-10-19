# -*- coding: UTF-8 -*-
"""Defines the CLI for displaying information about OneFS nodes"""
from collections import OrderedDict

import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.ascii_output import vm_table_view, columned_table


@click.command()
@click.option('-i', '--images', is_flag=True,
              help='Display the available versions of OneFS to deploy')
@click.pass_context
def onefs(ctx, images):
    """Display information about vOneFS nodes in your lab"""
    if images:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/onefs/image',
                            base_endpoint=False,
                            message='Collecting available versions of OneFS for deployment',
                            method='GET').json()['content']
        rows = []
        for img in info['image']:
            rows.append(img)
        table = get_formatted_table(sorted(rows))
        click.echo('\n{}\n'.format(table))
    else:
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/onefs',
                            message='Collecting information about your OneFS nodes',
                            method='GET').json()
        ordered_nodes = sort_node_list(info['content'])
        output = vm_table_view(ctx.obj.vlab_api, ordered_nodes)
        if not output:
            output = 'You do not own any OneFS nodes'
        click.echo(output)


def get_formatted_table(images):
    """Return a human friendly table of different OneFS deployment options

    :Returns: String

    :param images: The different images available, sorted by version number
    :type images: List
    """
    header_a = ['7.2.1 (Orca)',
                '8.0.0 (Riptide)',
                '8.0.1 (Halfpipe)',
                '8.1.0 (FreightTrain)',
               ]
    header_b = ['8.1.1 (Niijima)',
                '8.1.2 (Kanagawa)',
                '8.1.3 (Seismic)',
                '8.2.0 (Pipeline)'
               ]
    header_c = ['8.2.1 (Acela)',
                '8.2.2 (Beachcomber)',
                '9.0.0 (Cascades)',
                '9.1.0 (Deccan)'
               ]
    header_d = ['Update your vLab CLI']
    orca = sorted([x for x in images if '7.2.0' < x < '8.0.0.0' ])
    riptide = sorted([x for x in images if '7.2.1.9' < x < '8.0.1.0'])
    halfpipe = sorted([x for x in images if '8.0.0.9' < x < '8.1.0.0'])
    freight_train = sorted([x for x in images if '8.0.1.9'< x < '8.1.1.0'])
    niijima = sorted([x for x in images if '8.1.0.9' < x < '8.1.2.0'])
    kanagawa = sorted([x for x in images if '8.1.1.9' < x < '8.1.3.0'])
    seismic = sorted([x for x in images if '8.1.2.9' < x < '8.2.0.0'])
    pipeline = sorted([x for x in images if '8.2.0' <= x < '8.2.1.0'])
    acela = sorted([x for x in images if '8.2.1' < x < '8.2.2.0'])
    beachcomber = sorted([x for x in images if '8.2.2' < x < '8.2.3.0'])
    cascades = sorted([x for x in images if '9.0.0.0' <= x < '9.1.0.0'])
    deccan = sorted([x for x in images if '9.1.0' < x < '9.2.0.0'])
    net_new = sorted([x for x in images if '9.2.0' <= x])
    table_a = columned_table(header_a, [orca, riptide, halfpipe, freight_train])
    table_b = columned_table(header_b, [niijima, kanagawa, seismic, pipeline])
    table_c = columned_table(header_c, [acela, beachcomber, cascades, deccan])
    if net_new:
        table_d = columned_table(header_d, [net_new])
        table = '{}\n\n{}\n\n{}\n\n{}'.format(table_a, table_b, table_c, table_d)
    else:
        table = '{}\n\n{}\n\n{}'.format(table_a, table_b, table_c)
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
