#-*- coding: UTF-8 -*-
"""
This module is for setting up, and using SSH
"""
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


def generate_key_pair():
    """Create an SSH key pair

    :Returns: Tuple (public key, private key)
    """
    key = rsa.generate_private_key(backend=crypto_default_backend(),
                                   public_exponent=65537,
                                   key_size=2048)
    private_key = key.private_bytes(crypto_serialization.Encoding.PEM,
                                    crypto_serialization.PrivateFormat.PKCS8,
                                    crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH,
                                               crypto_serialization.PublicFormat.OpenSSH)
    return public_key, private_key
