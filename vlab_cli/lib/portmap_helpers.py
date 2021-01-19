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
        'centos': ['ssh', 'rdp'],
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
        'dataiq': ['ssh', 'https', 'rdp'],
        'dns': ['ssh', 'rdp'],
        'avamar': ['ssh', 'https', 'mgmt'],
        'avamarndmp' : ['ssh', 'mgmt'],
        'datadomain' : ['ssh', 'https']
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
    elif protocol == 'mgmt':
        port = get_mgmt_port(vm_type)
    else:
        raise RuntimeError("Unknown port for {} {}".format(vm_type, protocols))
    return port

def get_mgmt_port(vm_type):
    """Because some systems have an HTTPS based management interface."""
    mgmt_port_map = {
        'avamar' : 7543,
        'avamarndmp' : 7543,
    }
    return mgmt_port_map.get(vm_type.lower(), None)


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
    elif is_https(port_number):
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
        'dataiq' : 443,
        'avamar' : 443,
        'datadomain' : 443,
    }
    try:
        answer =  port_map[vm_type.lower()]
    except KeyError:
        answer = None
    return answer

def is_https(port):
    return port in [443, 9443, 8080, 7543]


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


def network_config_ok(ip, gateway, netmask):
    """Validate that the supplied IPv4 network config is valid.

    The return value is an error string. When the string has a length of zero,
    that indicates zero errors (i.e. the config is valid).

    :Returns: String

    :param ip: The IP to validate as part of a network config
    :type ip: String

    :param gateway: The default gateway of the subnet
    :type gateway: String

    :param netmask: The subnet mask of the network, i.e. 255.255.255.0
    :type netmask: String
    """
    error = ''
    # default gateway must within supplied subnet, so lets assume that is the network
    try:
        network = _to_network(gateway, netmask)
    except Exception:
        error = 'Default gateway {} not part of subnet {}'.format(gateway, netmask)
    else:
        if not ipaddress.IPv4Address(ip) in list(network):
            error = 'Static IP {} is not part of network {}. Adjust your netmask and/or default gateway'.format(ip, network)
    return error


def _to_network(gateway, netmask):
    """Convert an IP and subnet mask into CIDR format

    :Returns: ipaddress.IPv4Network

    :param gateway: The IPv4 address of the default gateway
    :type gateway: String

    :param netmask: The subnet mask of the network
    :type netmask: String
    """
    ipaddr = gateway.split('.')
    mask = netmask.split('.')
    # to calculate network start do a bitwise AND of the octets between netmask and ip
    net_start = '.'.join([str(int(ipaddr[x]) & int(mask[x])) for x in range(4)])
    bit_count = sum([bin(int(x)).count("1") for x in netmask.split('.')])
    cidr = '{}/{}'.format(net_start, bit_count)
    return ipaddress.IPv4Network(cidr)
