# -*- coding: UTF-8 -*-
"""
For interacting with your vLab Auth token
"""
import textwrap

import click

from vlab_cli.lib import tokenizer
from vlab_cli.lib.converters import epoch_to_date

@click.command()
@click.option('--show', is_flag=True, help='Display the contents of your authentication token')
@click.option('--delete', is_flag=True, help='Delete your token')
@click.option('--refresh', is_flag=True, help='Replace your current token with a new one')
@click.pass_context
def token(ctx, show, delete, refresh):
    """Your vLab authentication token"""
    if show:
        handle_show(ctx.obj.token_contents)
    elif delete:
        handle_delete(vlab_url=ctx.obj.vlab_url,
                      token=ctx.obj.token,
                      vlab_api=ctx.obj.vlab_api)
    elif refresh:
        handle_refresh(vlab_url=ctx.obj.vlab_url,
                       username=ctx.obj.username,
                       verify=ctx.obj.verify,
                       vlab_api=ctx.obj.vlab_api,
                       token=ctx.obj.token)
    else:
        raise click.ClickException('Must supply an argument. Use `-h` for help')


def handle_show(token_contents):
    """Prints the contents of the token in a pretty format.

    :returns: None

    :param token_contents: The decoded vLab auth token
    :type token_contents: Dictionary
    """
    info = """
    Username   : {}
    Issued by  : {}
    Issued at  : {}
    Expires at : {}
    Version    : {}
    Client IP  : {}
    """.format(token_contents['username'],
               token_contents['iss'],
               epoch_to_date(token_contents['iat']),
               epoch_to_date(token_contents['exp']),
               token_contents['version'],
               token_contents['client_ip'])
    click.echo(textwrap.dedent(info))



def handle_delete(vlab_url, token, vlab_api):
    """Remove the current token from local storage and the remote auth server

    :Returns: None

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String
    """
    try:
        tokenizer.delete(vlab_url)
        resp = vlab_api.delete('/api/2/auth/token', json={'token': token})
        resp.raise_for_status()
    except Exception as doh:
        raise click.ClickException(doh)
    else:
        click.echo('OK!')


def handle_refresh(vlab_url, username, verify, vlab_api, token):
    """Replace your token with a new one, and delete the old one from the auth server

    :Returns: None

    :param username: The name of the user to authenticate as.
    :type username: String

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String

    :param verify: Set to False if the vLab server is using a self-signed TLS cert
    :type verify: Boolean
    """
    try:
        token, decryption_key, algorithm  = tokenizer.create(username, vlab_url, verify)
        tokenizer.write(token, vlab_url, decryption_key, algorithm)
        resp = vlab_api.delete('/api/2/auth/token', json={'token': token})
        resp.raise_for_status()
    except Exception as doh:
        raise click.ClickException(doh)
    else:
        click.echo('OK!')
