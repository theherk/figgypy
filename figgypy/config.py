import logging
import os
import seria
import yaml

gpg_loaded = False
try:
    import gnupg
    gpg_loaded = True
except ImportError:
    logging.info('could not load gnupg, will be unable to unpack secrets')
    pass


log = logging.getLogger('figgypy')
if len(log.handlers) == 0:
    log.addHandler(logging.NullHandler())


class Config(object):
    """Configuration object

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

    def __init__(self, f):
        self._f = self._get_file(f)
        self._cfg = self._get_cfg(self._f)

    def _get_cfg(self, f):
        """Get configuration from config file"""
        try:
            with open(f, 'r') as _fo:
                try:
                    _seria_in = seria.load(_fo)
                    _y = _seria_in.dump('yaml')
                except Exception as e:
                    raise
        except IOError:
            raise FiggypyError("could not open configuration file")

        _cfg = yaml.load(_y)
        self._post_load_process(_cfg)
        for k, v in _cfg.items():
            setattr(self, k, v)

    def _post_load_process(self, cfg):
        gpg_decrypt(cfg)
        kms_decrypt(cfg, **self._aws_credentials)

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
