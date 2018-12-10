# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a ClarityNow instance"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='2.11.0', show_default=True,
              help='The version of ClarityNow to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ClarityNow instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new ClarityNow instance to')
@click.pass_context
def claritynow(ctx, name, image, external_network):
    """Create an instance of ClarityNow"""
    body = {'network': "{}_{}".format(ctx.obj.username, external_network),
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/claritynow',
                        message='Creating new instance of ClarityNow {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=resp.json()['content'])
    click.echo(output)
    info = """\n    ***IMPORTANT***

    ClarityNow requires a valid license to operate.
    Your ClarityNow server license will expire in 60 days.
    """
    click.secho(info, bold=True)
