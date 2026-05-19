# nuitka-project: --standalone
# nuitka-project: --include-data-file=icon.png=icon.png
# nuitka-project: --include-data-dir=warp_journal/frontend=warp_journal/frontend
# nuitka-project-set: PROJECT_VERSION = __import__("warp_journal").__version__.split("+")[0]
# nuitka-project-if: {OS} in ('Windows'):
#     nuitka-project: --mingw64
#     nuitka-project: --plugin-enable=tk-inter
#     nuitka-project: --windows-console-mode=disable
#     nuitka-project: --windows-icon-from-ico=icon.ico
#     nuitka-project: --windows-company-name=-
#     nuitka-project: --windows-product-name=Warp Journal
#     nuitka-project: --windows-file-description=Warp Journal
#     nuitka-project: --windows-product-version={PROJECT_VERSION}
#     nuitka-project: --windows-file-version={PROJECT_VERSION}

import logging

from warp_journal.server import Server
from warp_journal.util import get_usable_port, set_up_logging

def main():
    set_up_logging()
    port = get_usable_port()
    Server(port)
    logging.info('Quitting')

if __name__ == '__main__':
    main()
