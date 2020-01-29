# -*- coding: UTF-8 -*-
"""Defines the CLI for destroying a port mapping/forwarding rule"""
import click


from vlab_cli.lib.api import consume_task
from vlab_cli.lib.widgets import Spinner, typewriter
from vlab_cli.lib.click_extras import MandatoryOption, HiddenOption
from vlab_cli.lib.clippy import invoke_portmap_clippy
from vlab_cli.lib.portmap_helpers import (get_component_protocols, get_protocol_port,
                                          validate_ip, determine_which_ip, validate_ip)


@click.command()
@click.option('-a', '--ip-address',
              help='Explicitly supply the IP of the target VM')
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'https', 'rdp']),
              help='The protocol of the mapping rule to destory')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the VM that owns the rule')
@click.option('--override-port', cls=HiddenOption, type=int, default=0)
@click.pass_context
def portmap(ctx, name, protocol, ip_address, override_port):
    """Destroy a port mapping rule"""
    info = consume_task(ctx.obj.vlab_api,
                        endpoint='/api/1/inf/inventory',
                        message='Collecting information about your inventory',
                        method='GET').json()
    the_vm = info['content'].get(name, None)
    if the_vm is None:
        error = "You own no machine named {}. See 'vlab status' for help".format(name)
        raise click.ClickException(error)

    vm_type = the_vm['meta']['component']
    validate_ip(name, vm_type, the_vm['ips'], ip_address, the_vm['state'])
    target_addr = determine_which_ip(the_vm['ips'], ip_address)
    valid_protocols = get_component_protocols(vm_type)
    if not protocol or protocol not in valid_protocols:
        protocol = invoke_portmap_clippy(ctx.obj.username, vm_type, valid_protocols)
    target_port = get_protocol_port(vm_type, protocol)
    # Part of the fix for https://github.com/willnx/vlab/issues/61
    # This chunk of code allows users to delete port mapping rules
    # for the bad/wrong ESRS port.
    if the_vm['meta']['component'].lower() == 'esrs' and override_port:
        target_port = override_port

    with Spinner('Deleting port mapping rule to {} for {}'.format(name, protocol)):
        resp = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name': name, 'target_port' : target_port}).json()
        try:
            conn_port = list(resp['content']['ports'].keys())[0]
        except IndexError:
            # No such rule, but who cares? The target state (i.e. no rule) is true
            pass
        else:
            ctx.obj.vlab_api.delete('/api/1/ipam/portmap', json={'conn_port': int(conn_port)})
    click.echo('OK!')
