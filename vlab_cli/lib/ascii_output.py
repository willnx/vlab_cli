# -*- coding: UTF-8 -*-
"""This module formats common CLI output in a consistent format"""
import copy

from tabulate import tabulate


def format_machine_info(vlab_api, info):
    """Convert the deserialized JSON API response into a CLI friendly format

    :Returns: String

    :param vlab_api: An instantiated connection to the vLab server
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param info: The deserialized JSON API response from the vLab server
    :type info: Dictionary
    """
    rows = []
    kind = info['meta']['component']
    version = info['meta']['version']
    rows.append(['Type', ':', kind])
    rows.append(['Version', ':', version])
    rows.append(['State', ':', info['state']])
    rows.append(['IPs', ':', ' '.join(info['ips'])])
    rows.append(['Networks', ':', ','.join(info['networks'])])
    return tabulate(rows, tablefmt='plain')


def deployment_table(name, details, verbose=False):
    """Create an ASCII table displaying information about a deployment template.

    :Returns: String

    :param name: The name of the deployment template
    :type name: String

    :param details: Additional information about the template
    :type details: Dictionary

    :param verbose: Show extra information about the template.
    :type verbose: Boolean
    """
    owner = '{} {}'.format(details['owner'], details['email'])
    title = 'Name    : {}\nOwner   : {}\nSummary : {}'.format(name, owner, details['summary'])
    if verbose:
        header = ['Component', 'IP']
        body = [[x, details['machines'][x]['ip']] for x in details['machines'].keys()]
        components = '{}\n'.format(tabulate(body, headers=header, tablefmt='presto'))
    else:
        components = ''
    return '{}\n{}'.format(title, components)



def vm_table_view(vlab_api, info):
    """Create an ASCII table displaying information about virtual machines

    :Returns: String

    :param vlab_api: An instantiated connection to the vLab server
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param info: The mapping of VM name to general information about the VM
    :type info: Dictionary
    """
    vm_body = []
    vm_header = ['Name', 'IPs', 'Type', 'Version', 'Powered', 'Networks']
    for vm, data in info.items():
        body = {'url': data['console']}
        network = data.get('networks', ['?'])
        kind = data['meta']['component']
        version = data['meta']['version']
        power = data['state'].replace('powered', '')
        row = [vm, '\n'.join(data['ips']), kind, version, power, ','.join(network)]
        vm_body.append(row)
    if not vm_body:
        table = None
    else:
        table = tabulate(vm_body, headers=vm_header, tablefmt='presto')
    return table


def columned_table(header, columns):
    """Create an ASCII table by supplying a header and columns

    :Returns: String

    :param header: The headers of the table
    :type header: List

    :param columns: The different columns under each header
    :type columns: List
    """
    if not len(header) == len(columns):
        error = 'the number of columns must match the number of headers'
        raise ValueError(error)

    # Add extra elements so all columns are the same depth
    local_columns = copy.deepcopy(columns) # avoid side effects
    max_depth = len(max(columns, key=len))
    for idx, column in enumerate(local_columns):
        missing = max_depth - len(column)
        tmp = ['' for x in range(missing)]
        local_columns[idx] = column + tmp

    # Now transposing the columns to rows is easy!
    as_rows = zip(*local_columns)
    return tabulate(as_rows, headers=header, tablefmt='presto', numalign="center")
