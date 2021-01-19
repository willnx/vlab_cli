# -*- coding: UTF-8 -*-
"""Defines the CLI for creating a DataIQ instance"""
import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import typewriter
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_component_protocols, network_config_ok, get_protocol_port
from vlab_cli.lib.ascii_output import format_machine_info


@click.command()
@click.option('-i', '--image', default='1.0.0', show_default=True,
              help='The version of DataIQ to create')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the DataIQ instance in your lab')
@click.option('-s', '--static-ip', cls=MandatoryOption,
              help='The static IP to assign your DataIQ instance')
@click.option('-e', '--external-network', default='frontend', show_default=True,
              help='The public network to connect the new DataIQ instance to')
@click.option('-m', '--external-netmask', default='255.255.255.0', show_default=True,
              help='The subnet mask to use on the public network')
@click.option('-g', '--default-gateway', default='192.168.1.1', show_default=True,
              help='The default gateway to use on the public network')
@click.option('-d', '--dns-servers', default=['192.168.1.1'], multiple=True, show_default=True,
              help='The DNS server(s) to configure')
@click.option('-z', '--disk-size', default='250', type=click.Choice(['250', '500', '750']),
              help='The amount of GB to allocate for the DataIQ database')
@click.option('-p', '--cpu-count', default='4', type=click.Choice(['4', '8', '12']),
              help='The number of CPU cores to allocate to the VM')
@click.option('-r', '--ram', default='32', type=click.Choice(['32', '64', '96']),
              help='The number of GB of RAM/memory to allocate')
@click.pass_context
def dataiq(ctx, name, image, external_network, external_netmask, default_gateway,
           dns_servers, static_ip, disk_size, cpu_count, ram):
    """Create an instance of DataIQ"""
    error = network_config_ok(static_ip, default_gateway, external_netmask)
    if error:
        raise click.ClickException(error)
    body = {'network': external_network,
            'name': name,
            'image': image,
            'static-ip': static_ip,
            'default-gateway': default_gateway,
            'external-netmask': external_netmask,
            'dns-servers': dns_servers,
            'disk-size': int(disk_size),
            'cpu-count': int(cpu_count),
            'ram': int(ram)}
    resp = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/2/inf/dataiq',
                        message='Creating a new instance of DataIQ {}'.format(image),
                        body=body,
                        timeout=1800,
                        pause=5)
    data = resp.json()['content'][name]
    data['ips'] = [static_ip]
    vm_type = data['meta']['component']
    protocols = get_component_protocols(vm_type.lower())
    with Spinner('Creating port mapping rules for SSH, HTTPS, and RDP'):
        for protocol in protocols:
            target_port = get_protocol_port(vm_type.lower(), protocol)
            portmap_payload = {'target_addr' : static_ip, 'target_port' : target_port,
                               'target_name' : name, 'target_component' : vm_type}
            ctx.obj.vlab_api.post('/api/1/ipam/portmap', json=portmap_payload)

    output = format_machine_info(ctx.obj.vlab_api, info=data)
    click.echo(output)
    message = """\n    ***IMPORTANT***

    DataIQ still needs to be installed on your new instance.
    Please refer to the DataIQ Admin guide for installation directions:

    https://www.dell.com/support/home/us/en/19/product-support/product/data-iq/docs
    """
    click.secho(message, bold=True)
    typewriter("\nUse 'vlab connect dataiq --name {}' to access your new DataIQ instance".format(name))


def _setup_dataiq(vlab_api, name):
    all_ports = vlab_api.get('/api/1/ipam/portmap', params={'name': name}).json()['content']['ports']
    import pdb; pdb.set_trace()
    for conn_port, info in all_ports.items():
        if info['target_port'] == 22:
            break
    body = {'name': name, 'ssh-port': conn_port}
    resp = consume_task(valb_api,
                        endpoint='/api/2/inf/dataiq',
                        method='PUT',
                        message='Configuring DataIQ',
                        body=body,
                        timeout=900,
                        pause=5)
