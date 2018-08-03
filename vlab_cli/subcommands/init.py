# -*- coding: UTF-8 -*-
"""
Defines the CLI for initializing a virtual lab
"""
import time
import textwrap

import click

from vlab_cli.lib import ssh
from vlab_cli.lib.api import consume_task, block_on_tasks
from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.click_extras import HiddenOption


@click.command()
@click.option('--start-over', is_flag=True, help='Nuke your lab, and start all over')
@click.option('--switch', cls=HiddenOption, default='vLabSwitch')
@click.option('--wan', cls=HiddenOption, default='WAN-DHCP')
@click.pass_context
def init(ctx, start_over, switch, wan):
    """Initialize the virtual lab"""
    if start_over:
        click.secho('This will delete everything you own!', bold=True)
        click.confirm('Are you sure you want to continue?', abort=True)
        nuke_lab(ctx.obj.vlab_api, ctx.obj.username, switch, wan)
    else:
        init_lab(ctx.obj.vlab_api, ctx.obj.username, switch, wan)

    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/gateway',
                        message='Collecting info about your new lab',
                        method='GET')
    ips = [x for x in resp.json()['content']['ips'] if not ':' in x and not x.startswith('192.168.1')]
    if ips:
        ip = ips[0]
    else:
        ip = 'Error'
    msg = """
    Your lab is ready!

    To connect to your lab, SSH or RDP to {}
    You username will be {} and your default password is the letter "a"
    """.format(ip, ctx.obj.username)
    click.echo(textwrap.dedent(msg))
    click.secho("\nDon't be stupid. Change your password to something else when you login.\n", bold=True)

def nuke_lab(vlab_api, username, switch, wan):
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
                        endpoint='/api/1/inf/vlan',
                        message='Determining what networks you own',
                        method='GET')
    vlans = resp.json()['content']
    tasks = {}
    with Spinner('Deleting networks'):
        for vlan in vlans.keys():
            resp = vlab_api.delete('/api/1/inf/vlan', json={'vlan-name': vlan})
            tasks[vlan] = '/api/1/inf/vlan/task/{}'.format(resp.json()['content']['task-id'])
        block_on_tasks(vlab_api, tasks, pause=1)
    # old lab gone, make new lab
    click.echo('Finished deleting old lab. Initializing a new lab.')
    init_lab(vlab_api, username, switch, wan)


def init_lab(vlab_api, username, switch, wan):
    """Create a brand new virtual lab!

    :Returns: None

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param username: The name of the user deleting their lab
    :type username: String

    :param switch: The name of the network switch their networks are connected to
    :type switch: String

    :param wan: The name of the Wide Area Network their new lab should connect to
    :type wan: String
    """
    click.secho('This process can take upwards of 20 minutes', bold=True)
    with Spinner('Building your virtual lab'):
        _deploy_base(vlab_api, username, switch)
        _deploy_vms(vlab_api, username, wan)
    click.echo('OK!')


def _deploy_base(vlab_api, username, switch):
    """Create the inventory, and basic networks the user will need.

    :Returns: None

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param username: The name of the user deleting their lab
    :type username: String

    :param switch: The name of the network switch their networks are connected to
    :type switch: String
    """
    tasks = {}
    resp = vlab_api.post('/api/1/inf/inventory', auto_check=False)
    tasks['inventory'] = '/api/1/inf/inventory/task/{}'.format(resp.json()['content']['task-id'])

    body = {'vlan-name': '{}_frontend'.format(username), 'switch-name': switch}
    resp = vlab_api.post('/api/1/inf/vlan', json=body)
    tasks['frontend_network'] = '/api/1/inf/vlan/task/{}'.format(resp.json()['content']['task-id'])

    body = {'vlan-name': '{}_backend'.format(username), 'switch-name': switch}
    resp = vlab_api.post('/api/1/inf/vlan', json=body)
    tasks['backend_network'] = '/api/1/inf/vlan/task/{}'.format(resp.json()['content']['task-id'])
    block_on_tasks(vlab_api, tasks, auto_check=False, pause=1)


def _deploy_vms(vlab_api, username, wan):
    """Create the defalt gateway and jumpbox so users can access their new lab

    :Returns: None

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param username: The name of the user deleting their lab
    :type username: String

    :param wan: The name of the Wide Area Network their new lab should connect to
    :type wan: String
    """
    tasks = {}
    body = {'wan': wan, 'lan': '{}_frontend'.format(username)}
    resp = vlab_api.post('/api/1/inf/gateway', json=body)
    tasks['gateway'] = '/api/1/inf/gateway/task/{}'.format(resp.json()['content']['task-id'])

    body = {'network': '{}_frontend'.format(username)}
    resp = vlab_api.post('/api/1/inf/jumpbox', json=body)
    tasks['jumpbox'] = '/api/1/inf/jumpbox/task/{}'.format(resp.json()['content']['task-id'])
    block_on_tasks(vlab_api, tasks, auto_check=False)
