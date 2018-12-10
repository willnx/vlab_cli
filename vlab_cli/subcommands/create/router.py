# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a network router"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='1.1.8', show_default=True,
              help='The specific type & version of router to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name to give your new router')
@click.option('-e', '--networks', multiple=True)
@click.pass_context
def router(ctx, image, name, networks):
    """Create a new network router"""
    if len(networks) < 2:
        error = 'Routers must connect at least 2 networks, supplied {}: {}'.format(len(networks), ' '.join(networks))
        raise click.ClickException(error)
    elif len(networks) > 4:
        error = 'Routers can only connect at most 4 networks, supplied {}: {}'.format(len(networks), ' '.join(networks))
        raise click.ClickException(error)

    body = {'name': name, 'image': image, 'networks': ['{}_{}'.format(ctx.obj.username, x) for x in networks]}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/router',
                        message='Creating a new router for networks {}'.format(' '.join(networks)),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
