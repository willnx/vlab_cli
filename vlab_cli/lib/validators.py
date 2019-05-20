# -*- coding: UTF-8 -*-
"""TODO"""
import ipaddress


def to_network(ip, netmask):
    """Convert an IP and subnet mask into CIDR format

    :Returns: ipaddress.IPv4Network
    """
    ipaddr = ip.split('.')
    mask = netmask.split('.')
    # to calculate network start do a bitwise AND of the octets between netmask and ip
    net_start = '.'.join([str(int(ipaddr[x]) & int(mask[x])) for x in range(4)])
    bit_count = sum([bin(int(x)).count("1") for x in netmask.split('.')])
    cidr = '{}/{}'.format(net_start, bit_count)
    return ipaddress.IPv4Network(cidr)


def ext_network_ok(default_gateway, external_netmask, external_ip_range):
    """Determine if the supplied IP range is valid for a given gateway and subnet

    :Returns: Boolean
    """
    ext_network = to_network(default_gateway, external_netmask)
    ext_ip_low, ext_ip_high = [ipaddress.IPv4Address(x) for x in external_ip_range]
    high_ip_ok = ext_ip_high in ext_network
    low_ip_ok = ext_ip_low in ext_network
    answer = high_ip_ok and low_ip_ok
    return answer
