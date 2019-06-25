# -*- coding: UTF-8 -*-
"""Defines the CLI for deleting a OneFS node or cluster"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task, block_on_tasks
from vlab_cli.lib.click_extras import MutuallyExclusiveOption


@click.command()
@click.option('-n', '--name', cls=MutuallyExclusiveOption,
              mutually_exclusive=['cluster'],
              help='The name of the OneFS node in your lab to delete')
@click.option('-c', '--cluster', cls=MutuallyExclusiveOption,
              mutually_exclusive=['name'],
              help='The name of a cluster to delete (aka all nodes)')
@click.pass_context
def onefs(ctx, name, cluster):
    """Delete a OneFS node or cluster"""
    if name:
        delete_node(ctx.obj.vlab_api, name)
    elif cluster:
        delete_cluster(ctx.obj.vlab_api, cluster)
    else:
        raise click.ClickException('Must supply either param `--name` or `--cluster`')

def delete_node(vlab_api, name):
    """Destroy one specific node"""
    body = {'name': name}
    consume_task(vlab_api,
                 endpoint='/api/2/inf/onefs',
                 body=body,
                 message='Destroying OneFS node {}'.format(name),
                 method='DELETE')
    with Spinner('Deleting port mapping rules'):
        all_ports = vlab_api.get('/api/1/ipam/portmap', params={'name': name}).json()['content']['ports']
        for port in all_ports.keys():
            vlab_api.delete('/api/1/ipam/portmap', json={'conn_port': int(port)})
    click.echo('OK!')


def delete_cluster(vlab_api, cluster):
    """Destroy an entire OneFS cluster"""
    data = consume_task(vlab_api,
                        endpoint='/api/2/inf/onefs',
                        message='Looking up OneFS cluster {}'.format(cluster),
                        method='GET').json()
    nodes = _find_cluster_nodes(cluster, all_nodes=data['content'].keys())
    if not nodes:
        raise click.ClickException('No cluster named {} found'.format(cluster))
    tasks = {}
    with Spinner("Deleting cluster {}".format(cluster)):
        for node in nodes:
            body = {'name': node}
            resp = vlab_api.delete('/api/2/inf/onefs', json=body)
            tasks[node] = '/api/2/inf/onefs/task/{}'.format(resp.json()['content']['task-id'])
        block_on_tasks(vlab_api, tasks)
    with Spinner('Deleting port mapping rules'):
        for node in nodes:
            all_ports = vlab_api.get('/api/1/ipam/portmap', params={'name': node}).json()['content']['ports']
            for port in all_ports.keys():
                vlab_api.delete('/api/1/ipam/portmap', json={'conn_port': int(port)})
    click.echo('OK!')


def _find_cluster_nodes(cluster_name, all_nodes):
    """Given a cluster name, and a list of nodes owned, find the nodes that belong
    to that cluster

    :Returns: List

    :param cluster_name: The name of the OneFS cluster
    :type cluster_name: String

    :param all_nodes: Every OneFS node a user owns
    :type all_nodes: List
    """
    # Example of nodes in the cluster named "foo-bar"
    # foo-bar-1
    # foo-bar-10
    # foo-bar-100
    # Example of nodes in a different cluster
    # foo-barb-1
    # foo-bar
    # foobar
    # Must not falsely match foo-bar-baz-1, foobar, or foo-bar
    cluster_nodes = []
    cluster_name_has_dashes = bool(cluster_name.count('-'))
    for node in all_nodes:
        # perform 1 split at most
        chunked_name = node.rsplit('-', 1)
        # Avoid matching foo-bar the cluster with a single node named foo-bar
        if cluster_name_has_dashes and len(chunked_name) == 1:
            continue
        elif chunked_name[0] == cluster_name:
            cluster_nodes.append(node)
    return cluster_nodes
