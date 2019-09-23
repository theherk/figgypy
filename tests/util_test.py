# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.utils import bytes_to_native_str as n

from base64 import b64decode
from distutils.util import strtobool
import os
import unittest

import boto3

from figgypy.util import kms_encrypt


@unittest.skipUnless(strtobool(os.getenv('INTEGRATION', 'false')) == 1,
                     reason="credentials are required")
class TestEncryptIntegration(unittest.TestCase):
    def test_kms_encrypt(self):
        key = 'alias/figgypy-test'
        secret = 'correct horse battery staple'
        client = boto3.client('kms')
        encrypted = kms_encrypt(secret, key)
        dec_res = client.decrypt(CiphertextBlob=b64decode(encrypted))
        decrypted = n(dec_res['Plaintext'])
        assert decrypted == secret

    def test_ssm_store_parameter(self):
        return


if __name__ == '__main__':
    unittest.main()
