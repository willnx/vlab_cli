# -*- coding: UTF-8 -*-
"""
Defines the CLI for initializing a virtual lab
"""
import click

from vlab_cli.lib.click_extras import HiddenOption
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.api import consume_task, block_on_tasks
from vlab_cli.lib.configurizer import set_config, CONFIG_SECTIONS
from vlab_cli.lib.clippy.connect import invoke_config
from vlab_cli.lib.clippy.vlab_init import invoke_greeting, invoke_tutorial, invoke_init_done_help, invoke_eula


@click.command()
@click.option('--start-over', is_flag=True, help='Nuke your lab, and start all over')
@click.option('--switch', cls=HiddenOption, default='vLabSwitch')
@click.option('--wan', cls=HiddenOption, default='corpNetwork')
@click.pass_context
def init(ctx, start_over, switch, wan):
    """Initialize the virtual lab"""
    if start_over:
        nuke_lab(ctx.obj.vlab_api, ctx.obj.username, wan, switch, config=ctx.obj.vlab_config, log=ctx.obj.log)
    else:
        invoke_greeting(username=ctx.obj.username)
        accepts_terms = invoke_eula()
        if not accepts_terms:
            raise click.ClickException("Must agree to \"not ruin this for others\" to use vLab")
        invoke_tutorial()
        init_lab(ctx.obj.vlab_api, ctx.obj.username, wan, switch, config=ctx.obj.vlab_config, log=ctx.obj.log)


def nuke_lab(vlab_api, username, wan, switch, config, log):
    """Delete all VMs and Networks a user owns, and create a new one.

    :Returns: None

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param username: The name of the user deleting their lab
    :type username: String

    :param switch: The name of the network switch their networks are connected to
    :type switch: String

    :param wan: The name of the Wide Area Network their new lab should connect to
    :type wan: String

    :param config: The parsed configuration file used by the vLab CLI
    :type config: configparser.ConfigParser

    :param log: A logging object
    :type log: logging.Logger
    """
    consume_task(vlab_api,
                 endpoint='/api/1/inf/power',
                 body={'machine': 'all', 'power': 'off'},
                 message='Powering down your lab',
                 timeout=300,
                 pause=5)
    consume_task(vlab_api,
                 endpoint='/api/1/inf/inventory',
                 message='Destroying inventory',
                 method='DELETE')
    resp = consume_task(vlab_api,
                        endpoint='/api/2/inf/vlan',
                        message='Determining what networks you own',
                        method='GET')
    vlans = resp.json()['content']
    tasks = {}
    with Spinner('Deleting networks'):
        for vlan in vlans.keys():
            resp = vlab_api.delete('/api/2/inf/vlan', json={'vlan-name': vlan})
            tasks[vlan] = resp.links['status']['url']
        block_on_tasks(vlab_api, tasks, pause=1)
    typewriter('Finished deleting old lab. Initializing a new lab.')
    init_lab(vlab_api, username, wan, switch, config=config, log=log)


def init_lab(vlab_api, username, wan, switch, config, log):
    """Initialize the inventory, default networks, and gateway/firewall

    :Returns: None

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param username: The name of the user deleting their lab
    :type username: String

    :param switch: The name of the network switch their networks are connected to
    :type switch: String

    :param config: The parsed configuration file used by the vLab CLI
    :type config: configparser.ConfigParser

    :param log: A logging object
    :type log: logging.Logger
    """
    if not config:
        bad_config = True
    elif set(config.sections()) != CONFIG_SECTIONS:
        bad_config = True
    else:
        bad_config = False
    if bad_config:
        try:
            new_info = invoke_config()
        except Exception as doh:
            log.debug(doh, exc_info=True)
            raise click.ClickException(doh)
        else:
            set_config(new_info)

    with Spinner('Initializing your lab'):
        tasks = {}
        resp1 = vlab_api.post('/api/1/inf/inventory', auto_check=False)
        tasks['inventory'] = resp1.links['status']['url']

        body2 = {'vlan-name': 'frontend', 'switch-name': switch}
        resp2 = vlab_api.post('/api/2/inf/vlan', json=body2)
        tasks['frontend_network'] = resp2.links['status']['url']

        body3 = {'vlan-name': 'backend', 'switch-name': switch}
        resp3 = vlab_api.post('/api/2/inf/vlan', json=body3)
        tasks['backend_network'] = resp3.links['status']['url']
        block_on_tasks(vlab_api, tasks, auto_check=False, pause=1)

    body4 = {'wan': wan, 'lan': 'frontend'.format(username)}
    consume_task(vlab_api,
                 endpoint='/api/2/inf/gateway',
                 message='Deploying gateway',
                 method='POST',
                 body=body4,
                 timeout=1500,
                 pause=5,
                 auto_check=False)
    invoke_init_done_help()
