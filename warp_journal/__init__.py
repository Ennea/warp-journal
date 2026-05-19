try:
    import warp_journal._version as _version
    __version__ = _version.__version__
except ImportError:
    __version__ = '0+unknown'

__all__ = ["__version__"]
