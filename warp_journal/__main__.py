# nuitka-project: --standalone
# nuitka-project: --include-data-file=warp_journal/frontend/icon.png=icon.png
# nuitka-project: --include-data-dir=warp_journal/frontend=warp_journal/frontend
# nuitka-project-if: {OS} in ('Windows'):
#     nuitka-project: --mingw64
#     nuitka-project: --plugin-enable=tk-inter
#     nuitka-project: --windows-console-mode=disable
#     nuitka-project: --windows-icon-from-ico=icon.ico
#     nuitka-project: --windows-company-name=-
#     nuitka-project: --windows-product-name=Warp Journal
#     nuitka-project: --windows-file-description=Warp Journal
#     nuitka-project: --windows-product-version=1.2.0

import logging

from warp_journal.util import set_up_logging, get_usable_port
from warp_journal.server import Server

def main():
    set_up_logging()
    port = get_usable_port()
    Server(port)
    logging.info('Quitting')

if __name__ == '__main__':
    main()
