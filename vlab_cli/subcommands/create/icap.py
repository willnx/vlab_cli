# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an ICAP server"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='1.0.0', show_default=True,
              help='The ICAP server version to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ICAP server in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new ICAP server to')
@click.pass_context
def icap(ctx, name, image, external_network):
    """Create an ICAP Antivirus server"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/icap',
                        message='Creating a new ICAP server running version {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
    note = """\n    ***IMPORTANT***

    Before you can use your ICAP sever you must configure the IP the service listens on.
    To configure this, please open the console and:

    1) Launch the McAfee admin panel (look at the task bar)
    2) Right click on the ICAP service, and select "properties"
    3) Update the IP to match the IP of your new Windows machine
    4) Remember to click "OK" to save the setting
    """
    click.secho(note, bold=True)
