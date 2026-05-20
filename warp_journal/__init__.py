try:
    import warp_journal._version as _version
    __version__ = _version.__version__
except ImportError:
    __version__ = '0+unknown'


def main():
    import logging

    from .server import Server
    from .util import get_usable_port, set_up_logging

    set_up_logging()
    port = get_usable_port()
    Server(port)
    logging.info('Quitting')

__all__ = ["__version__", "main"]
