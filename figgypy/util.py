# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.utils import bytes_to_native_str as n

from base64 import b64encode
import os

import boto3


def kms_encrypt(value, key, aws_config=None):
    """Encrypt and value with KMS key.

    Args:
        value (str): value to encrypt
        key (str): key id or alias
        aws_config (optional[dict]): aws credentials
            dict of arguments passed into boto3 session
            example:
                aws_creds = {'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'region_name': 'us-east-1'}

    Returns:
        str: encrypted cipher text
    """
    aws_config = aws_config or {}
    aws = boto3.session.Session(**aws_config)
    client = aws.client('kms')
    enc_res = client.encrypt(KeyId=key, Plaintext=value)
    return n(b64encode(enc_res['CiphertextBlob']))


def ssm_store_parameter(name, value, key=None, aws_config=None):
    """Store a value in SSM Parameter Store.

    Args:
        name (str): name to store value under
        value (str): value to encrypt
        key (optional[str]): key id of kms key to use. if not passed in account
            default key will be used.
        aws_config (optional[dict]): aws credentials
            dict of arguments passed into boto3 session
            example:
                aws_creds = {'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'region_name': 'us-east-1'}

    Returns:
        str: name of parameter stored
    """
    aws_config = aws_config or {}
    aws = boto3.session.Session(**aws_config)
    client = aws.client('ssm')
    params = {
        Name: name,
        Value: value,
        Overwrite: True,
        Description: "Figgypy created/updated parameter",
        Type: "SecureString",
    }
    if key:
        params["KeyId"] = key
    client.put_parameter(**params)
    return name
