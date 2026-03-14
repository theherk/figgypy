from unittest.mock import MagicMock, patch

from figgypy.util import kms_encrypt, ssm_store_parameter


class TestKmsEncrypt:
    def test_kms_encrypt(self):
        with patch("figgypy.util.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_client.encrypt.return_value = {"CiphertextBlob": b"encrypted"}
            result = kms_encrypt("secret", "alias/test-key")
        assert isinstance(result, str)
        mock_client.encrypt.assert_called_once_with(KeyId="alias/test-key", Plaintext="secret")


class TestSsmStoreParameter:
    def test_ssm_store_parameter(self):
        with patch("figgypy.util.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            result = ssm_store_parameter("param-name", "param-value")
        assert result == "param-name"
        mock_client.put_parameter.assert_called_once()
        call_kwargs = mock_client.put_parameter.call_args[1]
        assert call_kwargs["Name"] == "param-name"
        assert call_kwargs["Value"] == "param-value"
        assert call_kwargs["Type"] == "SecureString"

    def test_ssm_store_parameter_with_key(self):
        with patch("figgypy.util.boto3") as mock_boto:
            mock_session = MagicMock()
            mock_boto.session.Session.return_value = mock_session
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            ssm_store_parameter("param-name", "param-value", key="alias/my-key")
        call_kwargs = mock_client.put_parameter.call_args[1]
        assert call_kwargs["KeyId"] == "alias/my-key"
