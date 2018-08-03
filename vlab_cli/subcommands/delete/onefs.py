# -*- coding: UTF-8 -*-
"""TODO"""
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
                 endpoint='/api/1/inf/onefs',
                 body=body,
                 message='Destroying OneFS node {}'.format(name),
                 method='DELETE')
    click.echo('OK!')

def delete_cluster(vlab_api, cluster):
    """Destroy an entire OneFS cluster"""
    data = consume_task(vlab_api,
                        endpoint='/api/1/inf/onefs',
                        message='Looking up OneFS cluster {}'.format(cluster),
                        method='GET').json()
    nodes = [x for x in data['content'].keys() if x.split('-')[0] == cluster]
    if not nodes:
        raise click.ClickException('No cluster named {} found'.format(cluster))
    tasks = {}
    with Spinner("Deleting cluster {}".format(cluster)):
        for node in nodes:
            body = {'name': node}
            resp = vlab_api.delete('/api/1/inf/onefs', json=body)
            tasks[node] = '/api/1/inf/onefs/task/{}'.format(resp.json()['content']['task-id'])
        block_on_tasks(vlab_api, tasks)
    click.echo('OK!')
