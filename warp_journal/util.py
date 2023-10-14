import logging
import os
import re
import shutil
import socket
import subprocess
import sys
import tkinter
from pathlib import Path
from tkinter import ttk
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def get_data_path():
    if sys.platform == 'win32':
        path = Path(os.environ['APPDATA']) / 'warp-journal'
    elif sys.platform == 'linux':
        if 'XDG_DATA_HOME' in os.environ:
            path = Path(os.environ['XDG_DATA_HOME']) / 'warp-journal'
        else:
            path = Path('~/.local/share/warp-journal').expanduser()
    elif sys.platform == 'darwin':
        if 'XDG_DATA_HOME' in os.environ:
            path = Path(os.environ['XDG_DATA_HOME']) / 'warp-journal'
        else:
            path = Path('~/Library/Application Support/warp-journal').expanduser()
    else:
        show_error('Warp Journal is only designed to run on Windows or Linux based systems.')

    # create dir if it does not yet exist
    if not path.exists():
        path.mkdir(parents=True)

    # path exists, but is a file
    if not path.is_dir():
        show_error(f'{path} already exists, but is a file.')

    return path

def get_cache_path():
    game_path = None
    try:
        game_path = Path(os.environ['GAME_PATH'])
    except KeyError:
        game_path = None

        try:
            log_path = Path(os.environ['USERPROFILE']) / 'AppData/LocalLow/Cognosphere/Star Rail/Player.log'
        except KeyError:
            logging.debug('USERPROFILE environment variable does not exist')
            return None

        if not log_path.exists():
            logging.debug('Player.log not found')
            return None

        regex = re.compile('Loading player data from (.+)/Games/StarRail_Data/data.unity3d')
        with log_path.open('r') as fp:
            for line in fp:
                match = regex.search(line)
                if match is not None:
                    game_path = match.group(1)
                    break

    if game_path is None:
        logging.debug('game path not found in output_log')
        return None

    # create a copy of the file so we can also access it while star rail is running.
    # python cannot do this without raising an error, and neither can the default
    # windows copy command, so we instead delegate this task to powershell's Copy-Item
    try:
        path = Path(game_path) / 'Games/StarRail_Data/webCaches/2.14.0.0/Cache/Cache_Data/data_2'
        logging.debug('cache path is: ' + str(path))
        if not path.exists():
            logging.debug('cache file does not exist')
            return None

        copy_path = get_data_path() / 'data_2'
        if sys.platform == 'win32':
            subprocess.check_output(f'powershell.exe -Command "Copy-Item \'{path}\' \'{copy_path}\'"', shell=True)
        else:
            shutil.copyfile(path, copy_path)
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        logging.error('Could not create copy of cache file')
        return None

    return copy_path

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
    port = 6193
    while is_port_in_use(port):
        # check if warp journal is already running on this port
        try:
            with urlopen(f'http://localhost:{port}/warp-journal', timeout=0.1) as _:
                pass
            show_error('Warp Journal is already running.')
        except (URLError, HTTPError):
            port += 1
            if port == 6203:
                show_error('No suitable port found.')

    return port

def show_error(message):
    logging.error(message)

    root = tkinter.Tk()
    root.title('Warp Journal')
    root.minsize(300, 0)
    root.resizable(False, False)
    root.iconphoto(False, tkinter.PhotoImage(file=Path(sys.path[0]) / 'icon.png'))

    frame = ttk.Frame(root, padding=10)
    frame.pack()
    ttk.Label(frame, text=message).pack()
    ttk.Frame(frame, height=5).pack()
    ttk.Button(frame, text='Okay', command=root.destroy).pack()

    # center the window
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry('+{}+{}'.format(int(screen_width / 2 - window_width / 2), int(screen_height / 2 - window_height / 2)))

    root.mainloop()
    logging.info('Quitting')
    sys.exit(1)
