from importlib import import_module


try:
    __version__ = import_module('warp_journal._version').__version__
except ImportError:
    __version__ = '0+unknown'

__all__ = ["__version__"]
