import os


def env_or_default(var, default=None):
    """Get environment variable or provide default.

    Args:
        var (str): environment variable to search for
        default (optional(str)): default to return
    """
    if var in os.environ:
        return os.environ[var]
    return default
