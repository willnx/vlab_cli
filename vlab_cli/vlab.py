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
from requests.exceptions import HTTPError

from vlab_cli import version
from vlab_cli.lib import tokenizer
from vlab_cli.lib.api import vLabApi
from vlab_cli.lib.logger import get_logger
from vlab_cli.lib.click_extras import GlobalContext, HiddenOption
from vlab_cli.subcommands import info, token, init, create, delete, show, power

# Setting these environment vars b/c Click needs it: http://click.pocoo.org/5/python3/
environ['LC_ALL'] = environ.get('LC_ALL', 'C.UTF-8')
environ['LANG'] = environ.get('LC_ALL', 'C.UTF-8')

# Settings and defaults
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VLAB_URL = 'https://vlab-dev.igs.corp'
VLAB_VERSION = version.__version__
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
@click.option('--debug', is_flag=True, cls=HiddenOption)
@click.pass_context
def cli(ctx, vlab_url, verify, vlab_username, verbose, debug):
    """CLI tool for interacting with your virtual lab"""
    log = get_logger(__name__, verbose=verbose, debug=debug)
    verify = not verify # invert for Beta
    if not vlab_url.startswith('https://'):
        # might have entered IP, or DNS FQDN
        vlab_url = 'https://{}'.format(vlab_url)

    # Get the token and decode it, assuming everything is OK
    try:
        log.info('Looking for a locally saved token')
        token, decryption_key, algorithm = tokenizer.read(vlab_url)
        token_contents = tokenizer.decode(token, vlab_url, decryption_key, algorithm)
    except (FileNotFoundError, PyJWTError, KeyError) as doh:
        log.info('No local token found')
        try:
            # Can't assume everything will go well here; might get file permission error
            # or user could enter a bad password
            log.info('Attempting to acquire new token')
            token, decryption_key, algorithm  = tokenizer.create(vlab_username, vlab_url, verify)
            log.info('Token acquired, decrypting it now')
            token_contents = tokenizer.decode(token, vlab_url, decryption_key, algorithm)
            log.info('Successfully decrypted token. Saving token to local file.')
            tokenizer.write(token, vlab_url, decryption_key, algorithm)
        except ValueError as doh:
            raise click.ClickException(doh)
        except Exception as doh:
            log.debug(doh, exc_info=True)
            raise click.ClickException(doh)
    except JSONDecodeError:
        log.info('Token file contains invalid JSON, automatically deleting file')
        tokenizer.destroy() # Not going to even try to fix the invalid JSON
        try:
            # Like before, can't assume everything will go OK...
            log.info("Successfully deleted token file")
            log.info('Attempting to acquire new token')
            token, decryption_key, algorithm  = tokenizer.create(vlab_username, vlab_url, verify)
            log.info('Success! Attempting to decode token')
            token_contents = tokenizer.decode(token, vlab_url, decryption_key, algorithm)
            log.info('Success! Attempting to write out new token')
            tokenizer.write(token, vlab_url, decryption_key, algorithm)
        except Exception as doh:
            log.info('Failed to automatically fix malformed token file')
            log.debug(doh, exc_info=True)
            raise click.ClickException(doh)
    except Exception as doh:
        log.debug(doh, exc_info=True)
        raise click.ClickException(doh)

    log.info('Initializing the vLab API object')
    vlab_api = vLabApi(server=vlab_url, token=token, verify=verify, log=log)
    ctx.obj = GlobalContext(log=log, vlab_api=vlab_api, vlab_url=vlab_url, token=token,
                            username=token_contents['username'], verify=verify,
                            token_contents=token_contents)
    log.info('Calling sub-command')

cli.add_command(info)
cli.add_command(token)
cli.add_command(init)
cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(power)
