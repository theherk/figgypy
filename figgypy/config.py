try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import logging
import os
import seria
import yaml

from figgypy import utils

log = logging.getLogger('figgypy')
if len(log.handlers) == 0:
    log.addHandler(logging.NullHandler())

GPG_IMPORTED = False
try:
    import gnupg
    GPG_IMPORTED = True
except ImportError:
    logging.info('could not load gnupg, will be unable to unpack secrets')


class FiggypyError(Exception):
    pass


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

    def __init__(self, f, gpg_config=None):
        self._gpg_config = gpg_config
        self._f = self._get_file(f)
        self._cfg = self._get_cfg(self._f)

    def _get_cfg(self, f):
        """Get configuration from config file"""
        try:
            with open(f, 'r') as _fo:
                try:
                    _seria_in = seria.load(_fo)
                    _y = _seria_in.dump('yaml')
                except Exception as err:
                    raise FiggypyError from err
        except IOError:
            raise FiggypyError("could not open configuration file")

        _cfg = yaml.load(_y)
        self._post_load_process(_cfg, self._gpg_config)
        for k, v in _cfg.items():
            setattr(self, k, v)

    def _decrypt_and_update(self, obj):
        """Decrypt and update configuration.

        Do this only from _post_load_process so that we can verify gpg
        is ready. If we did them in the same function we would end up
        calling the gpg checks several times, potentially, since we are
        calling this recursively.
        """
        if isinstance(obj, list):
            res_v = []
            for item in obj:
                res_v.append(self._decrypt_and_update(item))
            return res_v
        elif isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = self._decrypt_and_update(v)
        else:
            try:
                if 'BEGIN PGP' in obj:
                    try:
                        decrypted = self._gpg.decrypt(obj)
                        if decrypted.ok:
                            obj = decrypted.data.decode('utf-8')
                        else:
                            log.error("gpg error unpacking secrets %s" % decrypted.stderr)
                    except Exception as e:
                            log.error("error unpacking secrets %s" % e)
            except TypeError as e:
                log.info('Pass on decryption. Only decrypt strings')
        return obj

    def _post_load_process(self, cfg, gpg_config=None):
        if GPG_IMPORTED:
            if not gpg_config:
                gpg_config = {}
                defaults = {'homedir': '~/.gnupg/'}
                env_fields = {'homedir': 'FIGGYPY_GPG_HOMEDIR',
                              'binary': 'FIGGYPY_GPG_BINARY',
                              'keyring': 'FIGGYPY_GPG_KEYRING'}
                for k, v in env_fields.items():
                    gpg_config[k] = utils.env_or_default(
                        v, defaults[k] if k in defaults else None)
            try:
                self._gpg = gnupg.GPG(**gpg_config)
            except OSError:
                log.exception('failed to configure gpg, will be unable to decrypt secrets')
            return self._decrypt_and_update(cfg)
        return cfg

    def _get_file(self, f):
        """Get a config file if possible"""
        if os.path.isabs(f):
            return f
        else:
            for d in Config._dirs:
                _f = os.path.join(d, f)
                if os.path.isfile(_f):
                    return _f
            raise FiggypyError("could not find configuration file {} in dirs {}"
                               .format(f, Config._dirs))
