# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.utils import bytes_to_native_str as n

from base64 import b64decode
import os

import boto3
import pytest

from figgypy.utils import kms_encrypt


@pytest.mark.skipif(os.environ.get('INTEGRATION') is None,
                    reason="credentials are required")
class TestEncryptIntegration(object):
    def test_kms_encrypt(self):
        key = 'alias/figgypy-test'
        secret = 'test password 1234567890 !@#$%^&*()'
        client = boto3.client('kms')
        encrypted = kms_encrypt(secret, key)
        dec_res = client.decrypt(CiphertextBlob=b64decode(encrypted))
        decrypted = n(dec_res['Plaintext'])
        assert decrypted == secret
