# -*- coding: UTF-8 -*-
"""Defines the CLI for powering on/off/restart virtual machines"""
import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.click_extras import MandatoryOption


@click.group()
def power():
    """Change the power state of a VM in your lab"""
    pass


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM to turn on. Supply "all" to power on all VMs')
@click.pass_context
def on(ctx, name):
    """Power on a VM"""
    _change_power_state(ctx.obj.vlab_api, 'on', name)


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM to turn off. Supply "all" to power off all VMs')
@click.pass_context
def off(ctx, name):
    """Power off a VM; not graceful"""
    _change_power_state(ctx.obj.vlab_api, 'off', name)


@click.command()
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM to reboot. Supply "all" to reboot on all VMs')
@click.pass_context
def restart(ctx, name):
    """Power cycle a VM; not graceful"""
    _change_power_state(ctx.obj.vlab_api, 'restart', name)


def _change_power_state(api, power_state, machine_name):
    """The API for powering on/off/restarting is identical, so why duplicate code?

    :Returns: None

    :param api: A valid API connection to vLab
    :type vlab_api: vLabApi

    :param power_state: What to do, like power on/off/restart a VM
    :type power_state: String

    :param machine_name: The name of the VM to change the power state of
    :type machine_name: String
    """
    if power_state == 'restart':
        msg = 'Power cycling {}'.format(machine_name)
    else:
        msg = 'Powering {} {}'.format(power_state, machine_name)
    body = {'machine': machine_name, 'power': power_state}
    consume_task(api, endpoint='/api/1/inf/power', message=msg, body=body, timeout=600, pause=5)
    click.echo('OK!')


power.add_command(on)
power.add_command(off)
power.add_command(restart)
