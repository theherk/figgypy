# -*- coding: utf-8 -*-
"""Decrypt objects in Config."""
from __future__ import unicode_literals
from future.utils import bytes_to_native_str as n

from base64 import b64decode
import logging
import os

import boto3
from botocore.exceptions import ClientError, NoRegionError

from figgypy.exceptions import FiggypyError
from figgypy.utils import env_or_default

log = logging.getLogger('figgypy')

GPG_IMPORTED = False
try:
    import gnupg
    GPG_IMPORTED = True
except ImportError:
    logging.info('Could not load gnupg. Will be unable to unpack secrets.')


def gpg_decrypt(cfg, gpg_config=None):
    """Decrypt GPG objects in configuration.

    Args:
        cfg (dict): configuration dictionary
        gpg_config (dict): gpg configuration
            dict of arguments for gpg including:
                homedir, binary, and keyring (require all if any)
            example:
                gpg_config = {'homedir': '~/.gnupg/',
                              'binary': 'gpg',
                              'keyring': 'pubring.kbx'}

    Returns:
        dict: decrypted configuration dictionary

    The aim is to find in the dictionary items which have been encrypted
    with gpg, then decrypt them if possible.

    We will either detect the encryption based on the PGP block text or a
    user can create a key "_gpg" in which to store the data. Either case
    will work. In the case of the "_gpg" key all data at this level will
    be replaced with the decrypted contents. For example:

        {'component': {'key': 'PGP Block ...'}}

    will transform to:

        {'component': {'key': 'decrypted value'}}

    However:

        {'component': {'key': {'_gpg': 'PGP Block ...', 'nothing': 'should go here'}}}

    will transform to:

        {'component': {'key': 'decrypted value'}}
    """
    def decrypt(obj):
        """Decrypt the object.

        It is an inner function because we must first verify that gpg
        is ready. If we did them in the same function we would end up
        calling the gpg checks several times, potentially, since we are
        calling this recursively.
        """
        if isinstance(obj, list):
            res_v = []
            for item in obj:
                res_v.append(decrypt(item))
            return res_v
        elif isinstance(obj, dict):
            if '_gpg' in obj:
                try:
                    decrypted = gpg.decrypt(obj['_gpg'])
                    if decrypted.ok:
                        obj = n(decrypted.data.decode('utf-8').encode())
                    else:
                        log.error("gpg error unpacking secrets %s", decrypted.stderr)
                except Exception as err:
                    log.error("error unpacking secrets %s", err)
            else:
                for k, v in obj.items():
                    obj[k] = decrypt(v)
        else:
            try:
                if 'BEGIN PGP' in obj:
                    try:
                        decrypted = gpg.decrypt(obj)
                        if decrypted.ok:
                            obj = n(decrypted.data.decode('utf-8').encode())
                        else:
                            log.error("gpg error unpacking secrets %s", decrypted.stderr)
                    except Exception as err:
                        log.error("error unpacking secrets %s", err)
            except TypeError:
                log.debug('Pass on decryption. Only decrypt strings')
        return obj

    if GPG_IMPORTED:
        if not gpg_config:
            gpg_config = {}
            defaults = {'homedir': '~/.gnupg/'}
            env_fields = {'homedir': 'FIGGYPY_GPG_HOMEDIR',
                          'binary': 'FIGGYPY_GPG_BINARY',
                          'keyring': 'FIGGYPY_GPG_KEYRING'}
            for k, v in env_fields.items():
                gpg_config[k] = env_or_default(v, defaults[k] if k in defaults else None)
        try:
            gpg = gnupg.GPG(**gpg_config)
        except (OSError, RuntimeError):
            log.exception('Failed to configure gpg. Will be unable to decrypt secrets.')
        return decrypt(cfg)
    return cfg


def kms_decrypt(cfg, aws_config=None):
    """Decrypt KMS objects in configuration.

    Args:
        cfg (dict): configuration dictionary
        aws_config (dict): aws credentials
            dict of arguments passed into boto3 session
            example:
                aws_creds = {'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'region_name': 'us-east-1'}

    Returns:
        dict: decrypted configuration dictionary

    AWS credentials follow the standard boto flow. Provided values first,
    followed by environment, and then configuration files on the machine.
    Ideally, one would set up an IAM role for this machine to authenticate.

    The aim is to find in the dictionary items which have been encrypted
    with KMS, then decrypt them if possible.

    A user can create a key "_kms" in which to store the data. All data
    at this level will be replaced with the decrypted contents. For example:

        {'component': {'key': {'_kms': 'encrypted cipher text', 'nothing': 'should go here'}}}

    will transform to:

        {'component': {'key': 'decrypted value'}}

    To get the value to be stored as a KMS encrypted string:

        from figgypy.utils import kms_encrypt
        encrypted = kms_encrypt('your secret', 'your key or alias', optional_aws_config)
    """
    def decrypt(obj):
        """Decrypt the object.

        It is an inner function because we must first configure our KMS
        client. Then we call this recursively on the object.
        """
        if isinstance(obj, list):
            res_v = []
            for item in obj:
                res_v.append(decrypt(item))
            return res_v
        elif isinstance(obj, dict):
            if '_kms' in obj:
                try:
                    res = client.decrypt(CiphertextBlob=b64decode(obj['_kms']))
                    obj = n(res['Plaintext'])
                except ClientError as err:
                    if 'AccessDeniedException' in err.args[0]:
                        log.warning('Unable to decrypt %s. Key does not exist or no access', obj['_kms'])
                    else:
                        raise
            else:
                for k, v in obj.items():
                    obj[k] = decrypt(v)
        else:
            pass
        return obj
    try:
        aws = boto3.session.Session(**aws_config)
        client = aws.client('kms')
    except NoRegionError:
        log.info('Missing or invalid aws configuration. Will not be able to unpack KMS secrets.')
        return cfg
    return decrypt(cfg)
