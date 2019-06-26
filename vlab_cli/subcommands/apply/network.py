# -*- coding: UTF-8 -*-
"""Defines the CLI for updating the network a VM is connected to"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM to update')
@click.option('-w', '--new-network', cls=MandatoryOption,
              help='The name of network to connect the VM to')
@click.pass_context
def network(ctx, name, new_network):
    """Connect a Virtual Machine to a new front-end network"""
    update_endpoint = '/api/2/inf/{}/network'
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/inventory',
                        message='Looking up details for {}'.format(name),
                        method='GET')
    all_vms = resp.json()['content']
    for vm in all_vms:
        if vm == name:
            resource = all_vms[vm]['meta']['component'].lower()
            break
    else:
        error = "You own no VM named {}".format(name)
        raise click.ClickException(error)
    body = {'new_network': new_network, 'name' : name}
    consume_task(ctx.obj.vlab_api,
                 endpoint=update_endpoint.format(resource),
                 message='Connecting {} to network {}'.format(name, new_network),
                 body=body,
                 method='PUT',
                 base_endpoint=False)
    click.echo("OK!")
