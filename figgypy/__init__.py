"""figgypy is a simple configuration manager"""

__title__ = 'figgypy'
__author__ = 'Herkermer Sherwood'

from figgypy.config import Config

_config = None


def get_config():
    """Get the global configuration.

    For this to work you must first call figgypy.set_config. See set_config for help.

    The only purpose of this helper, is so that we can raise an error telling the library
    user that they must run figgypy.set_config first. If we had them use just use
    figgypy._config, the initial value of None would give no indication of how to
    initialize the Config object.
    """
    global _config
    if _config is None:
        raise ValueError('configuration not set; run figgypy.set_config first')
    return _config


def set_config(config):
    """Set a global config.

    This should work properly whether or not you import the full package namespace.
        # a.py
        import figgypy
        cfg = figgypy.Config()
        figgypy.set_config(cfg)

        # b.py
        import figgypy
        cfg = figgypy.get_config()

        import a
        import b
        # same cfg from a

    You will get new instances if you import from the namespace. i.e.
        # c.py
        from figgypy import Config, set_config
        cfg = Config()
        set_config(cfg)

        # d.py
        from figgypy import get_config
        cfg = get_config()

        import c
        import d
        # same cfg from c
    """
    global _config
    _config = config


def get(*args, **kwargs):
    """Get from config object by exposing Config.values.get method.

    dict.get() method on Config.values
    """
    global _config
    if _config is None:
        raise ValueError('configuration not set; must run figgypy.set_config first')
    return _config.get(*args, **kwargs)


__all__ = ['Config', 'get', 'get_config', 'set_config']
