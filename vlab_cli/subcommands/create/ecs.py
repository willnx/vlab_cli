# -*- coding: UTF-8 -*-
"""Defines the CLI for creating an ECS instances"""
import ipaddress

import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.ascii_output import format_machine_info
from vlab_cli.lib.portmap_helpers import https_to_port, get_ipv4_addrs


@click.command()
@click.option('-i', '--image', cls=MandatoryOption,
              help='The version of ECS to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ECS instance in your lab')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new ECS instance to')
@click.option('--skip-config', is_flag=True, show_default=True,
              help='Do not auto-configure the new ECS instance')
@click.pass_context
def ecs(ctx, name, image, external_network, skip_config):
    """Create an instance of Dell EMC Elastic Cloud Storage"""
    body = {'network': external_network,
            'name': name,
            'image': image}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/ecs',
                        message='Creating a new instance of ECS running {}'.format(image),
                        body=body,
                        timeout=900,
                        pause=5)
    data = resp.json()['content'][name]
    ipv4_addrs = get_ipv4_addrs(data['ips'])
    port_mapping = {}
    if ipv4_addrs:
        vm_type = data['meta']['component']
        https_port = https_to_port(vm_type.lower())
        with Spinner('Creating SSH and HTTPS port mapping rules'):
            for ipv4 in ipv4_addrs:
                portmap_payload = {'target_addr' : ipv4, 'target_port' : 22,
                                   'target_name' : name, 'target_component' : vm_type}
                new_port = ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload).json()['content']['conn_port']
                port_mapping[ipv4] = new_port
                portmap_payload['target_port'] = https_port
                ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    if not skip_config:
        resp = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/gateway',
                            message='Looking gateway information',
                            method='GET').json()['content']
        gateway_ips = [x for x in resp['ips'] if not x.startswith('192.168.') and not ':' in x]
        if gateway_ips:
            gateway_ip = gateway_ips[0]
        else:
            error = "Unable to determine IP of your vLab gateway. Is it powered on?"
            raise click.ClickException(error)
        ecs_ip = _determine_ip(port_mapping.keys())
        config_payload = {'name' : name, 'ssh_port': port_mapping[ecs_ip],
                          'gateway_ip' : gateway_ip, 'ecs_ip': ecs_ip}
        consume_task(ctx.obj.vlab_api,
                     endpoint='/api/2/inf/ecs/config',
                     message='Configuring your ECS instance',
                     method='POST',
                     body=config_payload,
                     base_endpoint=False,
                     timeout=900,
                     pause=5)
    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    if ipv4_addrs:
        typewriter("\nUse 'vlab connect ecs --name {}' to access your new ECS instance".format(name))



def _determine_ip(ip_addrs):
    """A heuristic for deciding which IP to bind ECS to.

    :Returns: String

    :Raises: click.Exception

    :param ip_addrs: All IPs assigned to the ECS VM
    :type ip_addrs: List

    :param ecs_ip: Optionally supply a specific IP. Note: ECS must already have
                   been assigned the supplied IP address.
    :type ecs_ip: String
    """
    docker_ip = ipaddress.ip_address('172.17.0.1')
    ipv4_addrs = [ipaddress.ip_address(x) for x in ip_addrs]
    ipv4_addrs = [x for x in ipv4_addrs if isinstance(x, ipaddress.IPv4Address) and x != docker_ip]
    if ipv4_addrs:
        for addr in ipv4_addrs:
            # Default network for vLab is 192.168.1.0/24
            if addr.exploded.startswith('192.168.1'):
                return addr.exploded
        else:
            # but maybe this ECS is for a custom network, so guess
            return ipv4_addrs[0].exploded
    else:
        error = 'ECS instance has no IPv4 address assigned: {}'.format(ip_addrs)
        raise click.Exception(error)
