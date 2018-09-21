# -*- coding: UTF-8 -*-
"""
Handles initial interaction with local vLab Auth tokens.

The tokenizer supports users interacting with multiple vLab servers by storing
the tokens in a JSON encoded file. The schema of that JSON file is as follows::

  {"version" : 1,
   "vlabs" : {
    "my-vlab.somewhere.com" : {
     "token" : "aaa.bbb.ccc",
     "key" : "Public decryption key",
     "algorithm" : "The JWT encryption method, i.e. HS256, RS512, etc"
    },
    "my-vlab-dev.somewhere.com" : {
     "token" : "ddd.eee.fff",
     "key" : "Public decryption key",
     "algorithm" : "The JWT encryption method, i.e. HS256, RS512, etc"
    }
   }
  }
"""
import os
import json
import time
import urllib3
from getpass import getpass

import jwt
import requests

from vlab_cli.lib.api import USER_AGENT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Creates path like /home/alice/.vlab/; must work with windows
TOKEN_DIR = os.path.join(os.path.expanduser('~'), '.vlab')
TOKEN_FILE = os.path.join(TOKEN_DIR, 'token.json')


def read(vlab_url):
    """Obtain the auth token, decryption key and algorithm for the supplied vLab server

    :Returns: Tuple

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String
    """
    with open(TOKEN_FILE) as the_file:
        contents = json.load(the_file)
    this_lab = contents['vlabs'][vlab_url]
    return this_lab['token'], this_lab['key'], this_lab['algorithm']


def decode(token, vlab_url, decryption_key, algorithm):
    """Convert the token from a string into a usable object

    :Returns: Dictionary

    :param token:
    :type token: String

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String

    :param decryption_key: The value to convert the token to plain text
    :type decryption_key: String

    :param algorithm: The algorithm used to when decrypting the token
    :type algorithm: String
    """

    data = jwt.decode(token, decryption_key, issuer=vlab_url,
                      algorithms=algorithm)
    remaining_time = data['exp'] - time.time()
    if remaining_time < 600:
        # it will expire in the next 10 minutes
        raise jwt.PyJWTError('Preemptive token expiration')
    else:
        return data


def write(token, vlab_url, decryption_key, algorithm):
    """Save the token to a local file.
    This avoids users having to enter their password every time they run a command.

    :Returns: None

    :param token: The encoded JWT
    :type token: String

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String

    :param decryption_key: The value to convert the token to plain text
    :type decryption_key: String

    :param algorithm: The algorithm used to when decrypting the token
    :type algorithm: String
    """
    with open(TOKEN_FILE) as the_file:
        contents = json.load(the_file)
    contents['vlabs'][vlab_url] = {}
    contents['vlabs'][vlab_url]['token'] = token
    contents['vlabs'][vlab_url]['key'] = decryption_key
    contents['vlabs'][vlab_url]['algorithm'] = algorithm
    with open(TOKEN_FILE, 'w') as the_file:
        json.dump(contents, the_file, indent=4, sort_keys=True)


def create(username, vlab_url, verify):
    """Obtain a new vLab Auth token, and create any local files for saving it.

    :Returns: String (the encoded JWT)

    :param username: The name of the user to authenticate as.
    :type username: String

    :param vlab_url: The specific vLab server to obtain a new token from.
    :type vlab_url: String

    :param verify: Set to False if the vLab server is using a self-signed TLS cert
    :type verify: Boolean
    """
    # Ensure vlab dir exists
    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    # Ensure we have the token file created
    try:
        with open(TOKEN_FILE):
            pass
    except FileNotFoundError:
        with open(TOKEN_FILE, 'w'):
            pass
        os.chmod(TOKEN_FILE, 0o600)
        with open(TOKEN_FILE, 'w') as the_file:
            json.dump({'version' : 1, 'vlabs': {}}, the_file, indent=4, sort_keys=True)

    # Now obtain a token
    password = getpass('Please enter your CORP domain password: ')
    resp = requests.post(vlab_url + '/api/2/auth/token',
                         json={'username': username, 'password': password},
                         headers={'User-Agent': USER_AGENT},
                         verify=verify)
    if resp.status_code == 401:
        error = 'Invalid password supplied for user {}'.format(username)
        raise ValueError(error)
    elif not resp.ok:
        resp.raise_for_status()
    else:
        new_token = resp.json()['content']['token']
        resp = requests.get(vlab_url + '/api/1/auth/key',
                            headers={'User-Agent': USER_AGENT},
                            verify=verify)
        data = resp.json()
        decryption_key = data['content']['key']
        algorithm = data['content']['algorithm']
        return new_token, decryption_key, algorithm


def truncate():
    """Empty all content within the token file

    :Returns: None

    This function exists because users can edit the token file, which is JSON
    encoded. If we cannot decode the JSON, it's likely a typo due to a human
    manually touching that file. So don't waste time trying to programmically fix
    the JSON, just nuke the contents (deleting their tokens) and start over.
    """
    with open(TOKEN_FILE, 'w'):
        # opening auto-truncates the file
        pass


def delete(vlab_url):
    """Read in the token file and remove the token for the given vlab_url

    :Returns: None

    :param vlab_url: The specific vLab server that issued the auth token
    :type vlab_url: String
    """
    with open(TOKEN_FILE, 'r') as the_file:
        contents = json.load(the_file)
    contents['vlabs'].pop(vlab_url, '')
    with open(TOKEN_FILE, 'w') as the_file:
        json.dump(contents, the_file)
