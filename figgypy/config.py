import logging
import os
import yaml

import seria

from figgypy.decrypt import (
    gpg_decrypt,
    kms_decrypt
)
from figgypy.exceptions import FiggypyError

log = logging.getLogger('figgypy')
if len(log.handlers) == 0:
    log.addHandler(logging.NullHandler())


class Config(object):
    """Configuration object

    Args:
        config_file (optional[str]): filename
            see config_file property for more details
        aws_config (optional[dict]): aws credentials
            see aws_config property for more details
            dict of arguments passed into boto3 session
            example:
                aws_creds = {'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'region_name': 'us-east-1'}
        gpg_config (optional[dict]): gpg configuration
            see gpg_config property for more details
            dict of arguments for gpg including:
                homedir, binary, and keyring (require all if any)
            example:
                gpg_config = {'homedir': '~/.gnupg/',
                              'binary': 'gpg',
                              'keyring': 'pubring.kbx'}
        decrypt_gpg (optional[bool]): decrypt gpg secrets
            see decrypt_gpg property for more details
            defaults to True
        decrypt_kms (optional[bool]): decrypt kms secrets
            see decrypt_kms property for more details
            defaults to True

    Returns:
        object: configuration object with 'values' dictionary

    move to config_file
    Object can be created with a filename only, relative path, or absolute path.
    If only name or relative path is provided, look in this order:

    1. current directory
    2. `~/.config/<file_name>`
    3. `/etc/<file_name>`

    It is a good idea to include you __package__ in the file name.
    For example, `cfg = Config(os.path.join(__package__, 'config.yaml'))`.
    This way it will look for your_package/config.yaml,
    ~/.config/your_package/config.yaml, and /etc/your_package/config.yaml.
    """
    _dirs = [
        os.curdir,
        os.path.join(os.path.expanduser("~"), '.config'),
        "/etc/"
    ]

    def __init__(self, config_file=None, aws_config=None, gpg_config=None,
                 decrypt_gpg=True, decrypt_kms=True):
        # Must initialize values first, since other setters may load self.values
        self.values = {}
        self._aws_config = aws_config
        self._gpg_config = gpg_config
        self._decrypt_gpg = decrypt_gpg
        self._decrypt_kms = decrypt_kms
        self._config_file = None
        # Load the file last so it can rely on the other properties.
        if config_file is not None:
            self.config_file = config_file

    @staticmethod
    def _find_file(f):
        """Find a config file if possible."""
        if os.path.isabs(f):
            return f
        else:
            for d in Config._dirs:
                _f = os.path.join(d, f)
                if os.path.isfile(_f):
                    return _f
            raise FiggypyError(
                "could not find configuration file {} in dirs {}"
                .format(f, Config._dirs)
            )

    def _load_file(self, f):
        """Get values from config file"""
        try:
            with open(f, 'r') as _fo:
                _seria_in = seria.load(_fo)
                _y = _seria_in.dump('yaml')
        except IOError:
            raise FiggypyError("could not open configuration file")
        self.values.update(yaml.load(_y))

    def _post_load_process(self):
        if gpg_decrypt:
            gpg_decrypt(self.values, self.gpg_config)
        if kms_decrypt:
            kms_decrypt(self.values, self.aws_config)
        for k, v in self.values.items():
            setattr(self, k, v)

    @property
    def aws_config(self):
        if self._aws_config is None:
            self._aws_config = {}
        return self._aws_config

    @aws_config.setter
    def aws_config(self, value):
        if not isinstance(value, dict):
            raise ValueError('aws_config must be a dict')
        # Further validation for dict contents may be warranted.
        self._aws_config = value
        if self.values:
            self._post_load_process()

    @property
    def config_file(self):
        """Configuration file.

        File can be located with a filename only, relative path, or absolute path.
        If only name or relative path is provided, look in this order:

        1. current directory
        2. `~/.config/<file_name>`
        3. `/etc/<file_name>`

        It is a good idea to include you __package__ in the file name.
        For example, `cfg = Config(os.path.join(__package__, 'config.yaml'))`.
        This way it will look for your_package/config.yaml,
        ~/.config/your_package/config.yaml, and /etc/your_package/config.yaml.
        """
        return self._config_file

    @config_file.setter
    def config_file(self, config_file):
        self._load_file(config_file)
        self._config_file = config_file
        self._post_load_process()

    @property
    def decrypt_gpg(self):
        return self._decrypt_gpg is not False

    @decrypt_gpg.setter
    def decrypt_gpg(self, value):
        self._decrypt_gpg = value is not False
        if self.values:
            self._post_load_process()

    @property
    def decrypt_kms(self):
        return self._decrypt_kms is not False

    @decrypt_kms.setter
    def decrypt_kms(self, value):
        self._decrypt_kms = value is not False
        if self.values:
            self._post_load_process()

    def get_value(self, *args, **kwargs):
        """Get from values dictionary by exposing self.values.get method.

        dict.get() method on Config.values
        """
        return self.values.get(*args, **kwargs)

    @property
    def gpg_config(self):
        if self._gpg_config is None:
            self._gpg_config = {}
        return self._gpg_config

    @gpg_config.setter
    def gpg_config(self, value):
        if not isinstance(value, dict):
            raise ValueError('gpg_config must be a dict')
        # Further validation for dict contents may be warranted.
        self._gpg_config = value
        if self.values:
            self._post_load_process()

    def set_value(self, key, value):
        """Set value in values dict."""
        self.values[key] = value

    def setup(self, config_file=None, aws_config=None, gpg_config=None,
              decrypt_gpg=True, decrypt_kms=True):
        """Make setup easier by providing a constructor method.

        Move to config_file
        File can be located with a filename only, relative path, or absolute path.
        If only name or relative path is provided, look in this order:

        1. current directory
        2. `~/.config/<file_name>`
        3. `/etc/<file_name>`

        It is a good idea to include you __package__ in the file name.
        For example, `cfg = Config(os.path.join(__package__, 'config.yaml'))`.
        This way it will look for your_package/config.yaml,
        ~/.config/your_package/config.yaml, and /etc/your_package/config.yaml.
        """
        if aws_config is not None:
            self.aws_config = aws_config
        if gpg_config is not None:
            self.gpg_config = gpg_config
        if decrypt_kms is not None:
            self.decrypt_kms = decrypt_kms
        if decrypt_gpg is not None:
            self.decrypt_gpg = decrypt_gpg
        # Again, load the file last so that it can rely on other properties.
        if config_file is not None:
            self.config_file = config_file
        return self
