from unittest.mock import MagicMock, patch

from figgypy.decrypt import gpg_decrypt, kms_decrypt, ssm_decrypt


class TestGpgDecrypt:
    def test_no_gpg_returns_cfg_unchanged(self):
        cfg = {"key": "value"}
        with patch("figgypy.decrypt.GPG_IMPORTED", False):
            result = gpg_decrypt(cfg)
        assert result == {"key": "value"}

    def test_decrypt_nested_dict(self):
        cfg = {"outer": {"inner": "plain"}}
        with patch("figgypy.decrypt.GPG_IMPORTED", False):
            result = gpg_decrypt(cfg)
        assert result == {"outer": {"inner": "plain"}}

    def test_non_string_passthrough(self):
        cfg = {"number": 42, "flag": True}
        with patch("figgypy.decrypt.GPG_IMPORTED", False):
            result = gpg_decrypt(cfg)
        assert result == {"number": 42, "flag": True}


class TestKmsDecrypt:
    def test_no_kms_key_passthrough(self):
        cfg = {"key": "value"}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_session.client.return_value = MagicMock()
            result = kms_decrypt(cfg)
        assert result == {"key": "value"}

    def test_kms_decrypt_value(self):
        cfg = {"db": {"pass": {"_kms": "dGVzdA=="}}}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_client.decrypt.return_value = {"Plaintext": b"decrypted_secret"}
            result = kms_decrypt(cfg)
        assert result == {"db": {"pass": "decrypted_secret"}}

    def test_kms_no_region_returns_cfg(self):
        from botocore.exceptions import NoRegionError

        cfg = {"key": "value"}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_boto.session.Session.side_effect = NoRegionError()
            result = kms_decrypt(cfg)
        assert result == {"key": "value"}


class TestSsmDecrypt:
    def test_no_ssm_key_passthrough(self):
        cfg = {"key": "value"}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_session.client.return_value = MagicMock()
            result = ssm_decrypt(cfg)
        assert result == {"key": "value"}

    def test_ssm_decrypt_value(self):
        cfg = {"db": {"pass": {"_ssm": "/myapp/db/pass"}}}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_client.get_parameter.return_value = {"Parameter": {"Value": "ssm_secret"}}
            result = ssm_decrypt(cfg)
        assert result == {"db": {"pass": "ssm_secret"}}

    def test_ssm_no_region_returns_cfg(self):
        from botocore.exceptions import NoRegionError

        cfg = {"key": "value"}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_boto.session.Session.side_effect = NoRegionError()
            result = ssm_decrypt(cfg)
        assert result == {"key": "value"}

    def test_decrypt_list(self):
        cfg = {"items": [{"_ssm": "/param1"}, {"_ssm": "/param2"}]}
        with patch("figgypy.decrypt.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_client.get_parameter.side_effect = [
                {"Parameter": {"Value": "val1"}},
                {"Parameter": {"Value": "val2"}},
            ]
            result = ssm_decrypt(cfg)
        assert result == {"items": ["val1", "val2"]}
