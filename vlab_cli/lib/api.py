# -*- coding: UTF-8 -*-
"""
A small abstraction to reduce boiler plate when working with the vLab RESTful API
"""
import uuid
import copy
import time
import urllib3
import pkg_resources

import click
import requests

from vlab_cli import version
from vlab_cli.lib.widgets import Spinner


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
USER_AGENT = 'vLab CLI {}'.format(version.__version__)


class vLabApi(object):
    """A small wrapper around requests.Session to handle boiler-plate code in API calls.

    This object will automatically set the token header for auth, and allows the
    caller to omit the server aspect of the URL. For instance, with standard
    requests an HTTP POST would look like this:

    .. code-block:: python

       vlab = requests.Session()
       resp = vlab.post('https://vlab.corp/api/1/inf/networks',
                  headers={'X-Auth': 'asdf.asdf.asdf},
                  json={'some': 'payalod'},
                  verify=False) # or omit if True...

    With this object, you can cut the boiler plate down to:

    .. code-block:: python

       vlab = vLabApi(server='vlab.corp', token='asdf.asdf.asdf', verify=False, log=log)
       resp = vlab.post('/api/1/inf/network', json={'some': 'payload'})

    :param server: The URL of the vLab server to connect to
    :type server: String

    :param token: The encoded JWT from the vLab Auth server
    :type token: String

    :param verify: Perform TLS host certificate validation
    :type verify: Boolean

    :param log: The logging object to aid in debugging
    :type log: logging.Logger
    """
    def __init__(self, server, token, verify=False, log=None):
        self._ipam_ip = None
        self._server = server
        self._session = requests.Session()
        self._header = {'X-Auth': token,
                        'User-Agent': USER_AGENT,
                        # Creates a random ID
                        # This object is only ever created once per invocation
                        # of a CLI command, regardless of how many API calls
                        # are made. This enables us to see how a simple CLI
                        # command might depend on multiple backend services.
                        'X-REQUEST-ID' : uuid.uuid4().hex}
        self._verify = verify if verify is False else True
        if log is None:
            raise ValueError('Must supply a log object')
        else:
            self._log = log

    def _call(self, method, endpoint, auto_check=True, **kwargs):
        """Does the actual HTTP API calling

        :Returns: requests.Response

        :Raises: requests.exceptions.HTTPError

        :param method: The HTTP method to invoke
        :type method: String

        :param endpoint: The API resource to call
        :type endpoint: String

        :param auto_check: Check the response code, and if needed raise an exception
        :type auto_check: Boolean

        :param **kwargs: Additional key-word arguments to send
        :type **kwargs: Dictionary
        """
        # API response contain the Links header. Testing for http here makes
        # it much easier for consume_task to rely on that header value.
        if endpoint.startswith('http'):
            url = endpoint
        else:
            url = build_url(self._server, endpoint)
        self._log.debug('Calling {} on {}'.format(method.upper(), url))
        headers = kwargs.get('headers', {})
        headers.update(self._header)
        caller = getattr(self._session, method)
        resp = caller(url, headers=headers, verify=self._verify, **kwargs)
        if not resp.ok and auto_check:
            self._log.debug("Call Failed: HTTP {}".format(resp.status_code))
            self._log.debug("Request ID: {}".format(self._header['X-REQUEST-ID']))
            self._log.debug("Response Headers:\n\t{}".format('\n\t'.join('{}: {}'.format(k, v) for k, v in resp.headers.items())))
            self._log.debug("Response body:\n\t{}\n".format(resp.content))
            try:
                error = resp.json()['error']
                if error is None:
                    error = resp.reason
            except Exception:
                error = resp.reason
            raise click.ClickException(error)
        return resp

    def get(self, endpoint, auto_check=True, **kwargs):
        """Perform an HTTP GET on an API end point

        :Returns: requests.Response

        :Raises: requests.exceptions.HTTPError

        :param endpoint: The API resource to call
        :type endpoint: String

        :param **kwargs: Additional key-word arguments to send
        :type **kwargs: Dictionary
        """
        return self._call(method='get', endpoint=endpoint, auto_check=auto_check, **kwargs)

    def post(self, endpoint, auto_check=True, **kwargs):
        """Perform an HTTP POST on an API end point

        :Returns: requests.Response

        :Raises: requests.exceptions.HTTPError

        :param endpoint: The API resource to call
        :type endpoint: String

        :param **kwargs: Additional key-word arguments to send
        :type **kwargs: Dictionary
        """
        return self._call(method='post', endpoint=endpoint, auto_check=auto_check, **kwargs)

    def put(self, endpoint, auto_check=True, **kwargs):
        """Perform an HTTP PUT on an API end point

        :Returns: requests.Response

        :Raises: requests.exceptions.HTTPError

        :param endpoint: The API resource to call
        :type endpoint: String

        :param **kwargs: Additional key-word arguments to send
        :type **kwargs: Dictionary
        """
        return self._call(method='put', endpoint=endpoint, auto_check=auto_check, **kwargs)

    def delete(self, endpoint, auto_check=True, **kwargs):
        """Perform an HTTP DELETE on an API end point

        :Returns: requests.Response

        :Raises: requests.exceptions.HTTPError

        :param endpoint: The API resource to call
        :type endpoint: String

        :param auto_check: Check the response code, and if needed raise an exception
        :type auto_check: Boolean

        :param **kwargs: Additional key-word arguments to send
        :type **kwargs: Dictionary
        """
        return self._call(method='delete', endpoint=endpoint, auto_check=auto_check, **kwargs)

    def unmap_port(self, target_addr, target_port):
        """Delete a port mapping/forwarding rule

        :Returns: None

        :Raises: ValueError

        :param target_addr: The IP address of the VM that owns the rule to delete
        :type target_addr: String

        :param target_port: The network port on the VM that will be un-mapped
        :type target_port: Integer
        """
        if self._ipam_ip is None:
            self._ipam_ip = self._find_ipam()
        url = 'https://{}/api/1/ipam/portmap'.format(self._ipam_ip)
        resp = self.get(url)
        firewall_rules = resp.json()['content']
        for conn_port in firewall_rules.keys():
            target_ip = firewall_rules[conn_port]['target_addr']
            target_port_number = firewall_rules[rule_id]['target_port']
            if target_ip == target_addr and target_port == target_port_number:
                break
        else:
            error = 'No rule found for IP {} and Port {}'.format(target_addr, target_port)
            raise ValueError(error)
        self.delete(url, json={'conn_port' : conn_port})

    def get_port_map(self):
        """Obtain all the port mapping/forwarding rules defined on the gateway

        :Returns: Dictionary
        """
        if self._ipam_ip is None:
            self._ipam_ip = self._find_ipam()
        url = 'https://{}/api/1/ipam/portmap'.format(self._ipam_ip)
        resp = self.get(url)
        return resp.json()['content']

    def delete_all_ports(self, vm_name):
        """Delete all the port mapping rules owned by a specific VM

        :Returns: None

        :param vm_name: The name of the VM
        :type vm_name: String
        """
        if self._ipam_ip is None:
            self._ipam_ip = self._find_ipam()
        url = 'https://{}/api/1/ipam/portmap'.format(self._ipam_ip)
        params = {'name': vm_name}
        all_ports = self.get(url, params=params).json()['content']
        for port in all_ports.keys():
            self.delete(url, json={'conn_port': port})

    def map_port(self, target_addr, target_port, target_name, target_component):
        """Create a port mapping rule in the IPAM server, and return the connection
        port.

        :Returns: Integer

        :Raises: requests.HTTPError

        :param target_addr: The IP address of the VM to create a mapping rule for
        :type target_addr: String

        :param target_port: The network port on the VM to create the mapping rule to
        :type target_port: Integer

        :param target_name: The name of the VM
        :type target_name: String

        :param target_component: The type of VM, i.e OneFS, InsightIQ, etc
        :type target_component: String
        """
        if self._ipam_ip is None:
            self._ipam_ip = self._find_ipam()
        url = 'https://{}/api/1/ipam/portmap'.format(self._ipam_ip)
        payload = {'target_addr' : target_addr,
                   'target_port' : target_port,
                   'target_name' : target_name,
                   'target_component' : target_component}
        resp = self.post(url, json=payload)
        conn_port = resp.json()['content']['conn_port']
        return conn_port

    def _find_ipam(self):
        """Discovers the IP of the IPAM server"""
        resp1 = self.get(endpoint='/api/2/inf/gateway', auto_check=False)
        status_url = resp1.links['status']['url']
        for _ in range(0, 300, 1):
            resp2 = self.get(status_url)
            if resp2.status_code == 202:
                time.sleep(1)
            else:
                break
        else:
            error = 'Timed out trying to discovery Gateway IP'.format(task)
            raise RuntimeError(error)
        all_ips = resp2.json()['content']['ips']
        ips = []
        for ip in all_ips:
            if ':' in ip:
                continue
            elif ip.startswith('127'):
                continue
            elif ip.startswith('192.168.'):
                continue
            else:
                ips.append(ip)
        if len(ips) != 1:
            error = "Unexpected IP(s) found on gateway: {}".format(ips)
            raise RuntimeError(error)
        return ips[0]


def build_url(base, *args):
    """Construct a valid URL from independent parts.

    Because urllib.parse.urljoin, for some damn reason, can't do this as succinctly.

    :Returns: String

    :Raises: ValueError

    :param base: The starting porition of the URL, like http://myserver.com.
    :type base: String

    :param *args: The URL parts you'd like to have joined together
    :type *args: List
    """
    if not base.lower().startswith('http'):
        raise ValueError('base must start with http, supplied {}'.format(base))
    tmp = [base.rstrip('/')]
    for item in args:
        tmp.append(item.strip('/'))
    return '/'.join(tmp)


def consume_task(vlab_api, endpoint, message, method='POST', body=None, params=None,
                 timeout=60, pause=1, auto_check=True, base_endpoint=True):
    """Automates processing tasks issued by the vLab API

    :Returns: requests.Response

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param endpoint: The URL that issued the task
    :type endpoint: String

    :param message: What to tell the end user while waiting on the task
    :type message: String

    :param timeout: How long to wait for the task to complete. Default 60 seconds
    :type timeout: Integer

    :param pause: How long to wait in between checking on the status of the task.
    :type pause: Integer

    :param auto_check: Check the response code, and if needed raise an exception
    :type auto_check: Boolean

    :param base_endpoint: Set to False if the end point is for <base>/image
    :type base_endpoint: Boolean
    """
    with Spinner(message):
        resp = vlab_api._call(method=method.lower(), endpoint=endpoint, auto_check=auto_check,
                              json=body, params=params)
        task = resp.json()['content']['task-id']
        if base_endpoint:
            url = '{}/task/{}'.format(endpoint, task)
        else:
            url = resp.links['status']['url']
        for _ in range(0, timeout, pause):
            resp = vlab_api.get(url)
            if resp.status_code == 202:
                time.sleep(pause)
            else:
                break
        else:
            error = 'Timed out on task {}'.format(task)
            raise click.ClickException(error)
        return resp

def block_on_tasks(vlab_api, tasks, timeout=900, pause=5, auto_check=True):
    """Wait for a group of tasks to complete

    The point of this function is to reduce boilerplate code when waiting on a
    group of tasks to complete. The expected dictionary supplied should be a
    mapping of a task to an API end point to call. It's most useful when you give
    the task a human friendly name, like "linuxVM" if the task is for creating/deleting
    a Linux VM.

    :Returns: None

    :Raises: click.ClickException (upon timeout)

    :param vlab_api: A valid API connection to vLab
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param tasks: The group of task items to API end points to wait on.
    :type tasks: Dictionary

    :param timeout: How long to wait for all tasks to complete
    :type timeout: Integer

    :param pause: How long to wait in between checking on the status of the task.
    :type pause: Integer

    :param auto_check: Check the response code, and if needed raise an exception
    :type auto_check: Boolean
    """
    info = {}
    local_tasks = copy.deepcopy(tasks) # this way there's no side-effect
    for _ in range(0, timeout, pause):
        time.sleep(pause)
        if not local_tasks:
            break
        for component, url in list(local_tasks.items()):
            resp = vlab_api.get(url, auto_check=auto_check)
            if resp.status_code == 202:
                continue
            else:
                info[component] = resp.json()
                local_tasks.pop(component)
    else:
        msg = 'Timed out waiting on componet(s): {}'.format(' '.join(local_tasks.keys()))
        raise click.ClickException(msg)
    return info
