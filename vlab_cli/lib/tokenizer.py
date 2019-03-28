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

from vlab_cli.lib.api import USER_AGENT, SSLContextAdapter

# Creates path like /home/alice/.vlab/; must work with windows
TOKEN_DIR = os.path.join(os.path.expanduser('~'), '.vlab')
TOKEN_FILE = os.path.join(TOKEN_DIR, 'token.json')


def get_token(vlab_url, vlab_username, verify, log):
    """Obtain an auth token and user information stored within

    Tokens are securely stored in a user's home directory. This avoid the client
    from having to obtain a new token with every invocation of the tool. This
    function handles the following conditions::

       1. Bootstrapping when no locally saved token exists
       2. A malformed token file
       3. An expired token

    :Returns: Tuple

    :param vlab_url: The URL of the vLab server
    :type vlab_url: String

    :param vlab_username: The name of the person accessing vLab
    :type vlab_username: String

    :param verify: Set to False if the server does not have a valid TLS certificate
    :type verify: Boolean,

    :param log: A logging object to aid in debugging
    :type log: logging.Logger
    """
    # Get the token and decode it, assuming everything is OK
    token, token_contents = None, None
    try:
        log.info('Looking for a locally saved token')
        token, decryption_key, algorithm = read(vlab_url)
        token_contents = decode(token, vlab_url, decryption_key, algorithm)
    except (FileNotFoundError, jwt.PyJWTError, KeyError) as doh:
        log.info('No local token found')
        try:
            # Can't assume everything will go well here; might get file permission error
            # or user could enter a bad password
            log.info('Attempting to acquire new token')
            token, decryption_key, algorithm  = create(vlab_username, vlab_url, verify)
            log.info('Token acquired, decrypting it now')
            token_contents = decode(token, vlab_url, decryption_key, algorithm)
            log.info('Successfully decrypted token. Saving token to local file.')
            write(token, vlab_url, decryption_key, algorithm)
        except ValueError as doh:
            raise doh
        except Exception as doh:
            log.debug(doh, exc_info=True)
            raise doh
    except json.JSONDecodeError:
        log.info('Token file contains invalid JSON, automatically deleting file')
        destroy() # Not going to even try to fix the invalid JSON
        try:
            # Like before, can't assume everything will go OK...
            log.info("Successfully deleted token file")
            log.info('Attempting to acquire new token')
            token, decryption_key, algorithm  = create(vlab_username, vlab_url, verify)
            log.info('Success! Attempting to decode token')
            token_contents = decode(token, vlab_url, decryption_key, algorithm)
            log.info('Success! Attempting to write out new token')
            write(token, vlab_url, decryption_key, algorithm)
        except Exception as doh:
            log.info('Failed to automatically fix malformed token file')
            log.debug(doh, exc_info=True)
            raise doh
    except Exception as doh:
        log.debug(doh, exc_info=True)
        raise doh
    return token, token_contents


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
    with requests.Session() as conn:
        conn.mount(vlab_url,  SSLContextAdapter())
        resp = conn.post(vlab_url + '/api/2/auth/token',
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
            resp = conn.get(vlab_url + '/api/1/auth/key',
                                headers={'User-Agent': USER_AGENT},
                                verify=verify)
            data = resp.json()
            decryption_key = data['content']['key']
            algorithm = data['content']['algorithm']
            return new_token, decryption_key, algorithm


def destroy():
    """Destroy the token file, and all of it's contents.

    :Returns: None

    This function exists because users can edit the token file, which is JSON
    encoded. If we cannot decode the JSON, it's likely a typo due to a human
    manually touching that file. So don't waste time trying to programmically fix
    the JSON, just nuke the contents (deleting their tokens) and start over.
    """
    os.remove(TOKEN_FILE)


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
