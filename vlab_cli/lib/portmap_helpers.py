# -*- coding: UTF-8 -*-
"""Centralized logic for mapping a component port number to a specific network protocol"""
import ipaddress

import click


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
            ipaddress.IPv4Address(requested_ip)
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
    found_ip = None
    for ip in vm_ips:
        try:
            ipaddress.IPv4Address(ip)
        except:
            continue
        else:
            found_ip = ip
            break
    if found_ip:
        return found_ip
    else:
        raise ClickException("Unable to find valid IPv4 address in {}".format(vm_ips))


def get_component_protocols(vm_type):
    """Lookup what protocols a specific component supports

    :Returns: List

    :param vm_type: The category of component (i.e. OneFS, InsightIQ, etc)
    :type vm_type: String
    """
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
        'winserver': ['rdp'],
        'esxi': ['ssh', 'https'],
    }
    return proto_map[vm_type.lower()]


def get_protocol_port(vm_type, protocol):
    """Return the specific network port a component uses for a provided protocol

    :Returns: Integer

    :param vm_type: The category of component (i.e. OneFS, InsightIQ, etc)
    :type vm_type: String

    :param protocol: The network protocol in question
    :type protocol: String
    """
    if protocol == 'https':
        port = https_to_port(vm_type)
    elif protocol == 'ssh' or protocol == 'scp':
        port = 22
    elif protocol == 'rdp':
        port = 3389
    return port


def port_to_protocol(vm_type, port_number):
    """Return the protocol when supplied with a given port value

    :Returns: String

    :param vm_type: The category of component (i.e. OneFS, InsightIQ, etc)
    :type vm_type: String

    :param port_number: The well-defined port number
    :type port_number: Integer
    """
    https = https_to_port(vm_type)
    if port_number == 22:
        return 'SSH/SCP'
    elif port_number == 3389:
        return 'RDP'
    elif port_number == https:
        return 'HTTPS'
    elif port_number == 443 and vm_type.lower() == 'esrs':
        # Fix for https://github.com/willnx/vlab/issues/61
        return 'HTTPS'
    else:
        raise RuntimeError('Unexpected port number: {}'.format(port_number))


def https_to_port(vm_type):
    """Because some component run HTTPS on an unprivileged port (i.e. not 443)

    :Returns: Integer

    :param vm_type: The category of component (i.e. OneFS, InsightIQ, etc)
    :type vm_type: String
    """
    port_map = {
        'claritynow' : 443,
        'ecs' : 443,
        'esrs' : 9443,
        'insightiq' : 443,
        'onefs' : 8080,
        'esxi' : 443,
    }
    try:
        answer =  port_map[vm_type.lower()]
    except KeyError:
        answer = None
    return answer


def get_ipv4_addrs(ips):
    """Obtain only the IPv4 addresses from a list of IPv4 and IPv6 addresses

    :Returns: List

    :param ips: The list of IPs a VM owns
    :type ips: List
    """
    ipv4_addrs = []
    for ip in ips:
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            continue
        else:
            ipv4_addrs.append(ip)
    return ipv4_addrs
