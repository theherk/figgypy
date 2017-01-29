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
        f (str): filename
            see below
        aws_config (dict): aws credentials
            dict of arguments passed into boto3 session
            example:
                aws_creds = {'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'region_name': 'us-east-1'}
        gpg_config (dict): gpg configuration
            dict of arguments for gpg including:
                homedir, binary, and keyring (require all if any)
            example:
                gpg_config = {'homedir': '~/.gnupg/',
                              'binary': 'gpg',
                              'keyring': 'pubring.kbx'}

    Returns:
        object: configuration object with attribute dictionary for each
            top level property

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

    def __init__(self, f, aws_config=None, gpg_config=None):
        self._aws_config = aws_config or {}
        self._gpg_config = gpg_config or {}
        self._f = self._get_file(f)
        self.values = self._load(self._f)

    def _load(self, f):
        """Get values from config file"""
        try:
            with open(f, 'r') as _fo:
                _seria_in = seria.load(_fo)
                _y = _seria_in.dump('yaml')
        except IOError:
            raise FiggypyError("could not open configuration file")

        _values = yaml.load(_y)
        self._post_load_process(_values, self._gpg_config)
        for k, v in _values.items():
            setattr(self, k, v)
        return _values

    def _post_load_process(self, obj, gpg_config=None):
        gpg_decrypt(obj, self._gpg_config)
        kms_decrypt(obj, self._aws_config)
        return obj

    def _get_file(self, f):
        """Get a config file if possible."""
        if os.path.isabs(f):
            return f
        else:
            for d in Config._dirs:
                _f = os.path.join(d, f)
                if os.path.isfile(_f):
                    return _f
            raise FiggypyError("could not find configuration file {} in dirs {}"
                               .format(f, Config._dirs))

    def get(self, *args, **kwargs):
        """Get from values dictionary by exposing self.values.get method.

        dict.get() method on Config.values
        """
        return self.values.get(*args, **kwargs)
