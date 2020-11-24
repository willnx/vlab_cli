"""Defines the CLI for managing deployment templates"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption, MultiValue


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the deployment template')
@click.option('-s', '--summary', cls=MultiValue,
              help='Changes the summary/desciption of the deployment template')
@click.option('-o', '--owner',
              help='Changes ownership of the deployment template')
@click.pass_context
def template(ctx, name, summary, owner):
    """Modify a deployment template you own"""
    body = {'template': name}
    if not (summary or owner):
        raise click.ClickException("Not enough arguments provided. Must change the summary or owner.")
    if summary:
        body['summary'] = ' '.join(summary)
    if owner:
        body['owner'] = owner
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/template',
                        message='Modifying deployment template {}'.format(name),
                        body=body,
                        method='PUT')
    typewriter('OK!')
