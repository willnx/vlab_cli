# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a network port mapping/forwarding rule"""
import ipaddress

import click

from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.clippy import invoke_portmap_clippy

@click.command()
@click.option('-a', '--ip-address',
              help='Explicitly supply the IP of the target VM')
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'https', 'rdp']),
              help='The protocol to create a mapping rule for')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM to create a rule for')
@click.pass_context
def portmap(ctx, name, protocol, ip_address):
    """Create a network port mapping/forwarding rule"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/inventory',
                        message='Collecting information about your inventory',
                        method='GET').json()
    the_vm = info['content'].get(name, None)
    if the_vm is None:
        error = 'You own no machine named {}. See `vlab status` for help'.format(name)
        raise click.ClickException(error)
    vm_type = the_vm['meta']['component']
    validate_ip(name, vm_type, the_vm['ips'], ip_address, the_vm['state'])
    target_addr = determine_which_ip(the_vm['ips'], ip_address)
    valid_protocols = get_component_protocols(vm_type)
    if not protocol or protocol not in valid_protocols:
        protocol = invoke_portmap_clippy(ctx.obj.username, vm_type, valid_protocols)
    target_port = get_protocol_port(vm_type, protocol)
    with Spinner('Creating port mapping rule to {} for {}'.format(name, protocol)):
        ctx.obj.vlab_api.map_port(target_addr, target_port, name, vm_type)
    typewriter("OK! Use 'vlab connect {} --protocol {}'' to access that machine".format(vm_type.lower(), protocol))


def validate_ip(vm_name, vm_type, vm_ips, requested_ip, vm_power_state):
    """Ensure that there is a valid IP to create a port mapping rule for.

    :Returns: None

    :Raises: click.ClickException

    :param vm_name: The name of the virtual machine (for better error messaging)
    :type vm_name: String

    :param vm_type: The kind of component to create a port mapping rule for
    :type vm_type: String

    :param requested_ip: An explicit IP the supplied by the user
    :type requested_ip: Enum(None, String)

    :param vm_power_state: Is the VM is poweredOn or poweredOff
    :type vm_power_state: String
    """
    if requested_ip is not None:
        try:
            ipaddress.ip_address(requested_ip)
        except ValueError as doh:
            raise click.ClickException(doh)

    if vm_type.lower() != 'onefs':
        if not vm_ips:
            # everything else has VMTools installed, so the server should return
            # an IP unless the VM isn't even powered on
            if vm_power_state == 'poweredoff':
                error = 'The VM must be powered on to create a rule. Try `vlab power on --name {}`'.format(vm_name)
                raise click.ClickException(error)
            else:
                error = 'Unable to map a port to a VM that has no IPs assigned.'
                raise click.ClickException(error)
        elif requested_ip and not (requested_ip in vm_ips):
            error = 'IP {} not owned by VM {}. VM has: {}'.format(requested_ip, vm_name, vm_ips)
            raise click.ClickException(error)
    elif requested_ip == None:
        error = 'Must provdie an IP to create a port mapping rule for a OneFS node'
        raise click.ClickException(error)


def determine_which_ip(vm_ips, requested_ip):
    """Determine which IP to create a mapping rule for

    :Returns: String (IP Address)

    :param vm_ips: All the IPs assigned to a virtual machine
    :type vm_ips: List

    :param requested_ip: An explicit IP the supplied by the user
    :type requested_ip: Enum(None, String)
    """
    if requested_ip:
        return requested_ip
    else:
        vm_ips[0]


def get_component_protocols(vm_type):
    """TODO"""
    proto_map = {
        'cee' : ['rdp'],
        'centos': ['ssh'],
        'claritynow': ['ssh', 'https', 'rdp'],
        'ecs' : ['ssh', 'https'],
        'esrs' : ['ssh', 'https'],
        'icap': ['rdp'],
        'insightiq': ['ssh', 'https'],
        'onefs': ['ssh', 'https'],
        'router': ['ssh'],
        'windows': ['rdp'],
        'winserver': ['rdp']
    }
    return proto_map[vm_type.lower()]


def get_protocol_port(vm_type, protocol):
    """TODO"""
    if protocol == 'https':
        port = https_to_port(vm_type)
    elif protocol == 'ssh':
        port = 22
    elif protocol == 'rdp':
        port = 3389
    return port


def https_to_port(vm_type):
    """TODO"""
    port_map = {
        'claritynow' : 443,
        'ecs' : 9443,
        'esrs' : 443,
        'insightiq' : 443,
        'onefs' : 8080,
    }
    return port_map[vm_type.lower()]
