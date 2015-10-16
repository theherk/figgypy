"""figgypy is a simple configuration manager"""

__title__ = 'figgypy'
__author__ = 'Herkermer Sherwood'

# bring the session handler into package namespace
from .config import Config

# only provide Config in *
__all__ = ['Config']
