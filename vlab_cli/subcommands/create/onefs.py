# -*- coding: UTF-8 -*-
"""Defines the CLI for creating OneFS nodes"""
import random
from collections import OrderedDict

import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.clippy import invoke_onefs_clippy
from vlab_cli.lib.ascii_output import vm_table_view
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import https_to_port
from vlab_cli.lib.api import block_on_tasks, consume_task
from vlab_cli.lib.widgets import Spinner, prompt, typewriter


@click.command()
@click.option('-i', '--image',
              help='The version of OneFS to create [required]')
@click.option('-n', '--name',
              help='The name of the vOneFS node in your lab [required]')
@click.option('-c', '--node-count', default=1, type=int, show_default=True,
              help='The number of nodes to create')
@click.option('-e', '--external', default='frontend', show_default=True,
              help='The public/external network to connect the node to')
@click.option('-t', '--internal', default='backend', show_default=True,
              help='The private/backend network to connect the node to')
@click.option('-x', '--external-ip-range', nargs=2,
              help='The range of IPs to assign to the public/external network [required]')
@click.option('-b', '--internal-ip-range', nargs=2, default='RANDOM', show_default=True,
              help='The range of IPs to assign to the private/backend network')
@click.option('-g', '--default-gateway', default='192.168.1.1', show_default=True,
              help='The default gateway of the public/external network')
@click.option('-s', '--smartconnect-ip', default='',
              help='Optionally provide the SmartConnect IP to be configured [optional]')
@click.option('-z', '--sc-zonename', default='',
              help='Optionally supply the SmartConnect Zone name to configure [optional]')
@click.option('-d', '--dns-servers', default=['10.7.190.6'], multiple=True, show_default=True,
              help='The DNS servers to use on the public/external network')
@click.option('-o', '--encoding', default='utf-8', show_default=True,
              help='The file system encoding to use on the new OneFS cluster')
@click.option('-m', '--external-netmask', default='255.255.255.0', show_default=True,
              help='The subnet mask to use on the public/external network')
@click.option('-a', '--internal-netmask', default='255.255.255.0', show_default=True,
              help='The subnet mask to use on the private/backend network')
@click.option('--skip-config', is_flag=True, show_default=True,
              help='Do not auto-configure the new OneFS cluster')
@click.pass_context
def onefs(ctx, name, image, node_count, external, internal, external_ip_range,
          internal_ip_range, default_gateway, smartconnect_ip, sc_zonename, dns_servers,
          encoding, external_netmask, internal_netmask, skip_config):
    """Create a vOneFS cluster. You will be prompted for any missing required parameters."""
    if node_count > 5:
        raise click.ClickException('You can only deploy a maximum of 5 nodes at a time')
    tasks = {}
    if skip_config and (name and image):
        bail = False
    elif not (name and image and external_ip_range):
        name, image, external_ip_range, bail = invoke_onefs_clippy(ctx.obj.username,
                                                                   name,
                                                                   image,
                                                                   external_ip_range,
                                                                   node_count,
                                                                   skip_config)
    else:
        bail = False
    if bail:
        raise click.ClickException('Not enough information supplied')
    if '192.168.1.1' in _generate_ips(external_ip_range[0], external_ip_range[1]):
        error = 'IP 192.168.1.1 is reserved for the gateway. Unable to assign to OneFS external network'
        raise click.ClickException(error)
    info = create_nodes(username=ctx.obj.username,
                        name=name,
                        image=image,
                        node_count=node_count,
                        external='{}_{}'.format(ctx.obj.username, external),
                        internal='{}_{}'.format(ctx.obj.username, internal),
                        vlab_api=ctx.obj.vlab_api)
    if not skip_config:
        config_nodes(cluster_name=name,
                     nodes=info.keys(),
                     image=image,
                     external_ip_range=external_ip_range,
                     internal_ip_range=internal_ip_range,
                     default_gateway=default_gateway,
                     smartconnect_ip=smartconnect_ip,
                     sc_zonename=sc_zonename,
                     dns_servers=dns_servers,
                     encoding=encoding,
                     external_netmask=external_netmask,
                     internal_netmask=internal_netmask,
                     vlab_api=ctx.obj.vlab_api)
        map_ips(vlab_api=ctx.obj.vlab_api, nodes=info.keys(), ip_range=external_ip_range)
    table = generate_table(vlab_api=ctx.obj.vlab_api, info=info)
    click.echo('\n{}\n'.format(table))
    if not skip_config:
        typewriter("Use 'vlab connect onefs --name {}' to connect to a specific node".format(list(info.keys())[0]))


def map_ips(vlab_api, nodes, ip_range):
    """TODO"""
    low_ip = min(ip_range)
    high_ip = max(ip_range)
    ips = _generate_ips(low_ip, high_ip)
    https_port = https_to_port('onefs')
    with Spinner('Creating SSH and HTTPS mapping rules for each node'):
        for ip, node in zip(ips, nodes):
            vlab_api.map_port(target_addr=ip,
                              target_port=22,
                              target_name=node,
                              target_component='OneFS')
            vlab_api.map_port(target_addr=ip,
                              target_port=https_port,
                              target_name=node,
                              target_component='OneFS')

def _generate_ips(start_ip, end_ip):
    """Given a starting and ending IP, return a list of all IPs within that range

    :Returns: List

    :param start_ip: The low end of the IP range
    :type start_ip: String

    :param end_ip: The high end of the IP range
    :type end_ip: String
    """
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range = []

    ip_range.append(start_ip)
    while temp != end:
       start[3] += 1
       for i in (3, 2, 1):
          if temp[i] == 256:
             temp[i] = 0
             temp[i-1] += 1
       ip_range.append(".".join(map(str, temp)))

    return ip_range


def create_nodes(username, name, image, external, internal, node_count, vlab_api):
    """Concurrently make all nodes

    :Returns: Dictionary

    :param username: The user who owns the new nodes
    :type username: String

    :param image: The image/version of OneFS node to create
    :type image: String

    :param external: The base name of the external network to connect the node(s) to
    :type external: String

    :param internal: The base name of the internal network to connect the node(s) to
    :type external: String

    :param node_count: The number of OneFS nodes to make
    :type node_count: Integer

    :param vlab_api: An instantiated connection to the vLab server
    :type vlab_api: vlab_cli.lib.api.vLabApi
    """
    tasks = {}
    node_v_nodes = 'node' if node_count == 1 else 'nodes'
    with Spinner('Deploying {} {} running {}'.format(node_count, node_v_nodes, image)):
        for idx in range(node_count):
            node_name = '{}-{}'.format(name, idx +1) # +1 so we don't have node-0
            body = {'name' : node_name,
                    'image': image,
                    'frontend': external,
                    'backend': internal,
                    }
            resp = vlab_api.post('/api/1/inf/onefs', json=body)
            tasks[node_name] = '/api/1/inf/onefs/task/{}'.format(resp.json()['content']['task-id'])
        info = block_on_tasks(vlab_api, tasks)
    return info


def config_nodes(cluster_name, nodes, image, external_ip_range, internal_ip_range,
                 default_gateway, smartconnect_ip, sc_zonename, dns_servers,
                 encoding, external_netmask, internal_netmask, vlab_api):
    """Take raw/new nodes, and turn them into a functional OneFS cluster

    :Returns: None
    """
    sorted_nodes = sorted(nodes, key=node_sorter)
    config_payload = make_config_payload(cluster_name=cluster_name,
                                         node_name=sorted_nodes.pop(0),
                                         image=image,
                                         external_ip_range=external_ip_range,
                                         internal_ip_range=internal_ip_range,
                                         default_gateway=default_gateway,
                                         smartconnect_ip=smartconnect_ip,
                                         sc_zonename=sc_zonename,
                                         dns_servers=dns_servers,
                                         encoding=encoding,
                                         external_netmask=external_netmask,
                                         internal_netmask=internal_netmask)
    join_payload = {'name' : '', 'cluster_name': cluster_name, 'join': True}
    consume_task(vlab_api,
                 endpoint='/api/1/inf/onefs/config',
                 message='Initializing cluster {}'.format(cluster_name),
                 body=config_payload,
                 timeout=900,
                 base_endpoint=False,
                 pause=5)
    for idx, node in enumerate(sorted_nodes):
        join_payload['name'] = node
        consume_task(vlab_api,
                     endpoint='/api/1/inf/onefs/config',
                     message='Joining node {} to cluster {}'.format(idx + 2, cluster_name),
                     body=join_payload,
                     timeout=900,
                     base_endpoint=False,
                     pause=5)



def make_config_payload(cluster_name, node_name, image, external_ip_range, internal_ip_range,
                        default_gateway, smartconnect_ip, sc_zonename, dns_servers,
                        encoding, external_netmask, internal_netmask):
    """Construct the request body content for making a new OneFS cluster

    :Returns: Dictionary
    """
    if ''.join(internal_ip_range).lower() == 'random':
        int_ip_low, int_ip_high = get_int_ips()
    else:
        try:
            int_ip_low, in_ip_high = internal_ip_range.split(' ')
        except ValueError:
            error = "Malformed value for Internal IPs supplied."
            raise click.ClickException(error)
    payload = {"name": node_name,
               "cluster_name": cluster_name,
               "encoding": encoding,
               "version": image,
               "ext_ip_high": str(max([ipaddress.ip_address[x] for x in external_ip_range])),
               "ext_ip_low": str(min([ipaddress.ip_address[x] for x in external_ip_range])),
               "ext_netmask": external_netmask,
               "int_ip_high": int_ip_high,
               "int_ip_low": int_ip_low,
               "int_netmask": internal_netmask,
               "dns_servers": dns_servers,
               "sc_zonename": sc_zonename,
               "smartconnect_ip": smartconnect_ip,
               "gateway": default_gateway,
              }
    return payload


def foo():
    """TODO"""
    pass


def get_int_ips():
    """Create a random range of backend/internal IPs to configure in OneFS

    :Returns: Tuple
    """
    # Stopping before 224 to avoid using reserved IP
    # https://en.wikipedia.org/wiki/Reserved_IP_addresses
    a = random.randint(1, 223)
    while a in (10, 192, 127):
        a = random.randint(1, 254)
    b = random.randint(1, 254)
    c = random.randint(1, 254)
    d = random.randint(1, 244)
    int_ip_low = '{}.{}.{}.{}'.format(a, b, c, d)
    int_ip_high = '{}.{}.{}.{}'.format(a, b, c, d + 10)
    return int_ip_low, int_ip_high


def generate_table(vlab_api, info):
    """Convert the new node information into a human friendly table

    :Returns: String

    :param vlab_api: An instantiated connection to the vLab server
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param info: A mapping of OneFS node names to node information
    :type info: Dictionary
    """
    ordered_nodes = OrderedDict()
    node_names = info.keys()
    ordered_names = sorted(node_names, key=node_sorter)
    for node_name in ordered_names:
        ordered_nodes[node_name] = info[node_name]['content'][node_name]
    table = vm_table_view(vlab_api, ordered_nodes)
    return table


def node_sorter(node_name):
    """A function to sort nodes vis-a-vis name"""
    return int(node_name.split('-')[-1])
