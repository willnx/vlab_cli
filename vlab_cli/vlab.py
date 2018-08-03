# -*- coding: UTF-8 -*-
"""
Entry point logic for the vLab CLI application
"""
import pkg_resources
from os import environ
from os.path import join
from getpass import getuser
from json import JSONDecodeError

import click
from jwt import PyJWTError

from vlab_cli.lib import tokenizer
from vlab_cli.lib.api import vLabApi
from vlab_cli.lib.logger import get_logger
from vlab_cli.lib.click_extras import GlobalContext
from vlab_cli.subcommands import info, token, init, create, delete, show, power

# Setting these environment vars b/c Click needs it: http://click.pocoo.org/5/python3/
environ['LC_ALL'] = environ.get('LC_ALL', 'C.UTF-8')
environ['LANG'] = environ.get('LC_ALL', 'C.UTF-8')

# Settings and defaults
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VLAB_URL = 'https://vlab-dev.igs.corp'
VLAB_VERSION = pkg_resources.get_distribution('vlab-cli').version
VLAB_VERIFY_HOSTNAME = True
VLAB_USER = getuser()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VLAB_VERSION)
@click.option('--vlab-url', default=VLAB_URL, help='The URL of the vLab server')
@click.option('--verify', is_flag=True, default=VLAB_VERIFY_HOSTNAME,
              help='Use this arg if the vLab server has a self-signed TLS cert')
@click.option('--vlab-username', default=VLAB_USER,
              help="In case the username you are logged in as is different from your corp name")
@click.option('--verbose', is_flag=True, help='Increase logging output')
@click.pass_context
def cli(ctx, vlab_url, verify, vlab_username, verbose):
    """CLI tool for interacting with your virtual lab"""
    log = get_logger(__name__, verbose=verbose)
    verify = not verify # invert for Beta
    if not vlab_url.startswith('https://'):
        # might have entered IP, or DNS FQDN
        vlab_url = 'https://{}'.format(vlab_url)

    # Get the token and decode it, assuming everything is OK
    try:
        token = tokenizer.read(vlab_url)
        token_contents = tokenizer.decode(token, vlab_url, verify)
    except (FileNotFoundError, PyJWTError, KeyError) as doh:
        if verbose:
            log.exception(verbose)
        try:
            # Can't assume everything will go well here; might get file permission error
            # or user could enter a bad password
            token  = tokenizer.create(vlab_username, vlab_url, verify)
            token_contents = tokenizer.decode(token, vlab_url, verify)
            tokenizer.write(token, vlab_url)
        except Exception as doh:
            raise click.ClickException(doh)
    except JSONDecodeError:
        tokenizer.truncate() # Not going to even try to fix the invalid JSON
        try:
            # Like before, can't assume everything will go OK...
            token  = tokenizer.create(vlab_username, vlab_url, verify)
            token_contents = tokenizer.decode(token, vlab_url, verify)
            tokenizer.write(token, vlab_url)
        except Exception as doh:
            raise click.ClickException(doh)
    except Exception as doh:
        if verbose:
            log.exception(doh)
        raise click.ClickException(doh)

    vlab_api = vLabApi(server=vlab_url, token=token, verify=verify)
    ctx.obj = GlobalContext(log=log, vlab_api=vlab_api, vlab_url=vlab_url, token=token,
                            username=token_contents['username'], verify=verify,
                            token_contents=token_contents)


cli.add_command(info)
cli.add_command(token)
cli.add_command(init)
cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(power)
