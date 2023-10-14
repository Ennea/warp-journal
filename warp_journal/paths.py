import logging
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from .error import panic

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
        panic('Warp Journal is only designed to run on Windows or Linux-based systems.')

    # ensure dir exists
    try:
        path.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        panic(f'{path} already exists, but is a file.')

    return path

def get_cache_path():
    if not (game_path := get_game_path()):
        return None

    web_cache_path = get_web_cache_path(game_path)
    if not web_cache_path:
        logging.debug('could not find latest webCaches subfolder')
        return None

    path = web_cache_path / 'Cache/Cache_Data/data_2'
    logging.debug('cache path is: ' + str(path))
    if not path.exists():
        logging.debug('cache file does not exist')
        return None

    if sys.platform == 'win32':
        # create a copy of the file so we can also access it while star rail is running.
        # python cannot do this without raising an error, and neither can the default
        # windows copy command, so we instead delegate this task to powershell's Copy-Item
        try:
            copy_path = get_data_path() / 'data_2'
            subprocess.check_output(f'powershell.exe -Command "Copy-Item \'{path}\' \'{copy_path}\'"', shell=True)
            return copy_path
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            logging.error('Could not create copy of cache file')
            return None
    else:
        return path

def get_game_path():
    """Retrieve the "game path".

    The "game path" is the one where the game data is put
    and not the folder of the launcher,
    which is the 'Games' subfolder on Windows.
    Since a custom launcher is generally used on Linux,
    the outer launcher folder doesn't exist there.
    """
    if 'GAME_PATH' in os.environ:
        # Allow some leeway for the envvar override
        game_path = Path(os.environ['GAME_PATH'])
        sub_path = game_path / 'Games'
        return sub_path if sub_path.exists() else game_path
    elif sys.platform == 'win32':
        return get_game_path_windows()
    elif sys.platform == 'linux':
        return get_game_path_linux()
    else:
        return None

def get_game_path_windows():
    if 'USERPROFILE' not in os.environ:
        logging.debug('USERPROFILE environment variable does not exist')
        return None

    log_path = Path(os.environ['USERPROFILE']) / 'AppData/LocalLow/Cognosphere/Star Rail/Player.log'
    if not log_path.exists():
        logging.debug('Player.log not found')
        return None

    regex = re.compile('Loading player data from (.+)/StarRail_Data/data.unity3d')
    with log_path.open() as fp:
        for line in fp:
            match = regex.search(line)
            if match is not None:
                return match.group(1)

    logging.debug('game path not found in output_log')
    return None

def get_game_path_linux():
    """Try to determine game folder from launcher configuration."""
    hsr_config_path = Path('~/.local/share/honkers-railway-launcher/config.json').expanduser()
    if not hsr_config_path.exists():
        logging.debug('launcher configuration not found')
        return None

    with hsr_config_path.open() as fp:
        config = json.load(fp)

    try:
        global_path = Path(config['game']['path']['global'])
        if global_path.exists():
            return global_path
        china_path = Path(config['game']['path']['china'])
        if china_path.exists():
            return china_path
    except KeyError:
        pass

    logging.debug('game folder configuration in launcher could not be found')
    return None

def get_web_cache_path(game_path):
    web_caches = game_path / 'StarRail_Data/webCaches/'
    versions = [
        (parts, p)
        for p in web_caches.iterdir()
        if p.is_dir() and len(parts := p.name.split('.')) > 1
    ]
    if not versions:
        return None
    versions.sort()
    return versions[-1][1]
