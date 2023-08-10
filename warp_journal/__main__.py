# nuitka-project: --standalone
# nuitka-project: --include-data-file=./icon.png=icon.png
# nuitka-project: --include-data-dir=./frontend=frontend
# nuitka-project-if: {OS} in ('Windows'):
#     nuitka-project: --mingw64
#     nuitka-project: --plugin-enable=tk-inter
#     nuitka-project: --windows-disable-console
#     nuitka-project: --windows-icon-from-ico=./icon.ico
#     nuitka-project: --windows-company-name=-
#     nuitka-project: --windows-product-name=Warp Journal
#     nuitka-project: --windows-file-description=Warp Journal
#     nuitka-project: --windows-product-version=1.0.1

import logging

from .util import set_up_logging, get_usable_port
from .server import Server

def main():
    set_up_logging()
    port = get_usable_port()
    Server(port)
    logging.info('Quitting')

if __name__ == '__main__':
    main()
