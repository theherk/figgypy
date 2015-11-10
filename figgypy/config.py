try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import logging
import os
import seria
import yaml

logger = logging.getLogger('figgypy')
if len(logger.handlers) == 0:
    logger.addHandler(logging.NullHandler())

gpg_loaded = False
try:
    import gnupg
    gpg_loaded = True
except ImportError:
    logging.info('could not load gnupg, will be unable to unpack secrets')
    pass


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
                            logger.error("gpg error unpacking secrets %s" % decrypted.stderr)
                    except Exception as e:
                            logger.error("error unpacking secrets %s" % e)
            except TypeError as e:
                logger.info('Pass on decryption. Only decrypt strings')
        return obj

    def _post_load_process(self, cfg):
        if gpg_loaded:
            gpgbinary='gpg'
            gnupghome=None
            try:
                if 'FIGGY_GPG_BINARY' in os.environ:
                    gpgbinary = os.environ['FIGGY_GPG_BINARY']
                if 'FIGGY_GPG_HOME' in os.environ:
                    gnupghome = os.environ['FIGGY_GPG_HOME']
                self._gpg = gnupg.GPG(gpgbinary=gpgbinary, gnupghome=gnupghome)
                return self._decrypt_and_update(cfg)
            except OSError as e:
                if len(e.args) == 2:
                    if (e.args[1] == 'The system cannot find the file specified'
                        or 'No such file or directory' in e.args[1]):
                        # frobnicate
                        if not 'FIGGY_GPG_BINARY' in os.environ:
                            logger.error(
                                "cannot find gpg executable, path=%s, try setting GPG_BINARY env variable" % gpgbinary)
                        else:
                            logger.error("cannot find gpg executable, path=%s" % gpgbinary)
                else:
                    logger.error("cannot setup gpg, %s" % e)
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
