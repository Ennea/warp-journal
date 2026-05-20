# nuitka-project: --standalone
# nuitka-project: --include-data-file=icon.png=icon.png
# nuitka-project: --include-data-dir=warp_journal/frontend=warp_journal/frontend
# nuitka-project-set: PROJECT_VERSION = ".".join(filter(None, __import__("re").match(r"^(\d+)\.(\d+)\.(\d+)(?:\.post\d+)?(?:\.dev(\d+))?", __import__("warp_journal").__version__).groups()))
# nuitka-project-if: {OS} in ('Windows'):
#     nuitka-project: --msvc=latest
#     nuitka-project: --plugin-enable=tk-inter
#     nuitka-project: --windows-console-mode=disable
#     nuitka-project: --windows-icon-from-ico=icon.ico
#     nuitka-project: --windows-company-name=-
#     nuitka-project: --windows-product-name=Warp Journal
#     nuitka-project: --windows-file-description=Warp Journal
#     nuitka-project: --windows-product-version={PROJECT_VERSION}
#     nuitka-project: --windows-file-version={PROJECT_VERSION}

import warp_journal


if __name__ == '__main__':
    warp_journal.main()
