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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

from vlab_cli import version
from vlab_cli.lib.widgets import Spinner


USER_AGENT = 'vLab CLI {}'.format(version.__version__)


class SSLContextAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.load_default_certs() # this loads the OS defaults on Windows
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)


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
        self._server = server
        self._session = requests.Session()
        self._session.mount(server, SSLContextAdapter())
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

    @property
    def server(self):
        return self._server

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
        if resp.status_code == 503:
            self._log.debug("Retrying API call")
            resp = self._exponential_backoff(self, caller, url, headers, **kwargs)
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

    def _exponential_backoff(self, caller, url, headers, **kwargs):
        """Retries the API call a several times until the response is not HTTP 503.
        The delay between retrying grows exponentially.

        :Returns: requests.Response
        """
        total_retries = 5
        some_time = 1
        for _ in range(total_retries):
            time.sleep(some_time)
            resp = caller(url, headers=headers, verify=self._verify, **kwargs)
            if resp.status_code != 503:
                break
            some_time = some_time *  2
        return resp, some_time


    def close(self):
        """Terminate the TCP connection with the vLab server"""
        self._session.close()

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
            url = resp.links['status']['url']
        for _ in range(0, timeout, pause):
            resp = vlab_api.get(url, auto_check=auto_check)
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
