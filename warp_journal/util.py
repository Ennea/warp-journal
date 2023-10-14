import logging
import os
import socket
import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from .error import panic
from .paths import get_data_path


def set_up_logging():
    log_level = logging.DEBUG if 'DEBUG' in os.environ else logging.INFO
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(filename=(get_data_path() / 'warp-journal.log'), format=log_format, level=log_level)

    # add a stream handler for log output to stdout
    root_logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)

    logging.info('Starting Warp Journal')

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def get_usable_port():
    for port in range(6193, 6193 + 10):
        if not is_port_in_use(port):
            return port
        # check if warp journal is already running on this port
        try:
            with urlopen(f'http://localhost:{port}/warp-journal', timeout=0.1) as _:
                return port
            panic('Warp Journal is already running.')
        except (URLError, HTTPError):
            continue

    panic('No suitable port found.')
