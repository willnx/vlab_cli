# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a deployment template"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption, MultiValue


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name for the deployment template.')
@click.option('-m', '--machines', nargs=-1, cls=MultiValue,
              help='The VMs in your lab to include in the new template.')
@click.option('-s', '--summary', nargs=-1, cls=MultiValue,
              help='A short description of the new template.')
@click.pass_context
def template(ctx, name, machines, summary):
    """Create a deployment template"""
    if not machines:
        msg = 'Must supply at least 1 VM'
        raise click.ClickException(msg)
    elif not summary:
        msg = 'Must supply a summary/description for the template.'
        raise click.ClickException(msg)

    # Instead of asking the user to provide portmap info, just query for the
    # existing rules and use those. What could go wrong? :P
    body = {'name' : name, 'summary' : ' '.join(summary), 'machines' : machines}
    portmaps = []
    with Spinner('Looking portmap rules for machines'):
        for machine in machines:
            resp = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name' : machine})
            data = [x for x in resp.json()['content']['ports'].values()]
            if data:
                ports = [x['target_port'] for x in data]
                target_addr = [x['target_addr'] for x in data][0]
                port_map = {'name': machine, 'target_addr': target_addr, 'target_ports': ports}
                portmaps.append(port_map)
    body['portmaps'] = portmaps

    # Actually make the template!
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/template',
                        message='Creating a new deployement template named {}'.format(name),
                        body=body,
                        timeout=3600,
                        pause=5)
    click.echo("Successfully created template {}".format(name))
    click.echo("Deploy {0} by running 'vlab create deployment --image {0}'".format(name))
