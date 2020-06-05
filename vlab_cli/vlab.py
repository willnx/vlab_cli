# -*- coding: UTF-8 -*-
"""
Entry point logic for the vLab CLI application
"""
import atexit
import pkg_resources
from os import environ
from os.path import join
from getpass import getuser
from json import JSONDecodeError

import click
from jwt import PyJWTError
from requests.exceptions import HTTPError

from vlab_cli import version
from vlab_cli.lib import widgets
from vlab_cli.lib.api import vLabApi
from vlab_cli.lib.logger import get_logger
from vlab_cli.lib.tokenizer import get_token
from vlab_cli.lib.new_cli import handle_updates
from vlab_cli.lib.configurizer import get_config, set_config
from vlab_cli.lib.click_extras import GlobalContext, HiddenOption
from vlab_cli.subcommands import status, token, init, create, delete, show, power, connect, apply

# Setting these environment vars b/c Click needs it: http://click.pocoo.org/5/python3/
environ['LC_ALL'] = environ.get('LC_ALL', 'C.UTF-8')
environ['LANG'] = environ.get('LC_ALL', 'C.UTF-8')

# Settings and defaults
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VLAB_URL = 'https://vlab.emc.com'
VLAB_VERSION = version.__version__
VLAB_SKIP_VERIFY_HOSTNAME = False
VLAB_USER = getuser()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VLAB_VERSION)
@click.option('--vlab-url', default=VLAB_URL, show_default=True,
              help='The URL of the vLab server')
@click.option('--skip-verify', is_flag=True, default=VLAB_SKIP_VERIFY_HOSTNAME, show_default=True,
              help='Use this arg if the vLab server has a self-signed TLS cert')
@click.option('--vlab-username', default=VLAB_USER, show_default=True,
              help="In case the username you are logged in as is different from your corp name")
@click.option('--verbose', is_flag=True, help='Increase logging output')
@click.option('--no-scroll', '-o', is_flag=True,
              help='Output messages all at once')
@click.option('-s', '--skip-update-check', is_flag=True, help="Don't check for and updated vLab CLI")
@click.option('--debug', is_flag=True, cls=HiddenOption)
@click.pass_context
def cli(ctx, vlab_url, skip_verify, vlab_username, verbose, no_scroll, skip_update_check, debug):
    """CLI tool for interacting with your virtual lab"""
    log = get_logger(__name__, verbose=verbose, debug=debug)
    verify = not skip_verify # inverted because ``requests`` is 'opt-out' of hostname verification
    if not vlab_url.startswith('https://'):
        # might have entered IP, or DNS FQDN
        vlab_url = 'https://{}'.format(vlab_url)
    widgets.NO_SCROLL_OUTPUT = no_scroll
    try:
        the_token, token_contents = get_token(vlab_url, vlab_username, verify=verify, log=log)
    except Exception as doh:
        log.debug(doh, exc_info=True)
        raise click.ClickException(doh)
    if the_token is None and token_contents is None:
        log.debug('Tokenizer returned null token and contents')
        raise RuntimeError("Invalid token created by library")

    # Subcommands the rely on the config must address it being None
    config = get_config()
    log.info('Initializing the vLab API object')
    vlab_api = vLabApi(server=vlab_url, token=the_token, verify=verify, log=log)
    atexit.register(vlab_api.close)
    ctx.obj = GlobalContext(log=log, vlab_api=vlab_api, vlab_url=vlab_url, token=the_token,
                            username=token_contents['username'], verify=verify,
                            token_contents=token_contents,
                            vlab_config=config)
    log.info("Checking for updates")
    handle_updates(vlab_api, config, skip_update_check)
    log.info('Calling sub-command')


cli.add_command(status)
cli.add_command(token)
cli.add_command(init)
cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(power)
cli.add_command(connect)
cli.add_command(apply)
