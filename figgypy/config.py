import logging
import io
import os
import seria
import yaml

logger = logging.getLogger('figgypy')
logger.addHandler(logging.NullHandler())

gpg_loaded = False
try:
    import gnupg
    gpg_loaded = True
except ImportError:
    logging.info('could not load gnupg, will be unable to unpack secrets')
    pass


class FiggyPyError(Exception):
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
            raise FiggyPyError("could not open configuration file")

        _cfg = yaml.load(_y)
        self._post_load_process(_cfg)
        for k, v in _cfg.items():
            setattr(self, k, v)

    def _post_load_process(self, config):
        if gpg_loaded and "_secrets" in config:
            gpgbinary = 'gpg'
            try:
                if 'GPG_BINARY' in os.environ:
                    gpgbinary = os.environ['GPG_BINARY']
                self.gpg = gnupg.GPG(gpgbinary=gpgbinary)
            except WindowsError as e:
                if len(e.args) == 2:
                    if e.args[1] == 'The system cannot find the file specified':
                        if not 'GPG_BINARY' in os.environ:
                            logger.error("cannot find gpg executable, path=%s, try setting GPG_BINARY env variable" %gpgbinary)
                        else:
                            logger.error("cannot find gpg executable, path=%s" %gpgbinary)
                else:
                    logger.error("cannot setup gpg, %s" %e)
                return
            except Exception as e:
                logger.error("cannot setup gpg, %s" %e)

            try:
                packed = self.gpg.decrypt(config['_secrets'])
                if packed.ok:
                    secret_stream = io.StringIO(str(packed))
                    _seria_in = seria.load(secret_stream)
                    config['secrets'] = yaml.load(_seria_in.dump('yaml'))
                else:
                    logger.error("gpg error unpacking secrets %s" % packed.stderr)
            except Exception as e:
                logger.error("error unpacking secrets %s" % packed.stderr)
        return config

    def _get_file(self, f):
        """Get a config file if possible"""
        if os.path.isabs(f):
            return f
        else:
            for d in Config._dirs:
                _f = os.path.join(d, f)
                if os.path.isfile(_f):
                    return _f
            raise FiggyPyError("could not find configuration file {} in dirs {}"
                               .format(f, Config._dirs))
