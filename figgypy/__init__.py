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


def set_config(*args, **kwargs):
    """Set a global config.

    See help(figgypy.config.Config) for full signature.

    For this to work properly you must import the full package namespace.
        # a.py
        import figgypy
        cfg = figgypy.set_cfg(cfg_file)
        # cfg is from the file you passed in

        # b.py
        import figgypy
        cfg = figgypy.get_cfg()
        # cfg is from the file you passed in still

    You will get new instances if you import from the namespace. i.e.
        # a.py
        from figgypy import set_cfg
        cfg = set_cfg(cfg_file)
        # cfg is the file you passed in

        # b.py
        from figgypy import get_cfg
        cfg = get_cfg()
        # cfg will raise an error since it has not yet been set
    """
    global _config
    _config = Config(*args, **kwargs)
    return _config


def get(*args, **kwargs):
    """Get from config object by exposing Config.values.get method.

    dict.get() method on Config.values
    """
    global _config
    if _config is None:
        raise ValueError('configuration not set; must run figgypy.set_config first')
    return _config.get(*args, **kwargs)


__all__ = ['Config', 'get', 'get_config', 'set_config']
