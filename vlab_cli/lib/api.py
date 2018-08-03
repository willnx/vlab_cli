# -*- coding: UTF-8 -*-
"""
A small abstraction to reduce boiler plate when working with the vLab RESTful API
"""
import copy
import time
import urllib3
import pkg_resources

import click
import requests

from vlab_cli.lib.widgets import Spinner


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
USER_AGENT = 'vLab CLI {}'.format(pkg_resources.get_distribution('vlab-cli').version)

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

       vlab = vLabApi(server='vlab.corp', token='asdf.asdf.asdf', verify=False)
       resp = vlab.post('/api/1/inf/network', json={'some': 'payload'})
    """
    def __init__(self, server, token, verify=False):
        self._server = server
        self._session = requests.Session()
        self._header = {'X-Auth': token, 'User-Agent': USER_AGENT}
        self._verify = verify if verify is False else True

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
        url = build_url(self._server, endpoint)
        headers = kwargs.get('headers', {})
        headers.update(self._header)
        caller = getattr(self._session, method)
        resp = caller(url, headers=headers, verify=self._verify, **kwargs)
        if not resp.ok and auto_check:
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
            # strip /image off the URL; using the rstrip method would convert
            # /api/1/inf/cee/image to /api/1/inf/c
            url = '{}/task/{}'.format(endpoint[:len(endpoint) - 6], task)
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
