from __future__ import annotations

import logging
import re
from urllib.parse import urlparse, parse_qs

from .paths import get_cache_path
from .exceptions import AuthTokenExtractionError, LogNotFoundError

__all__ = [
    'find_gacha_url',
    'extract_region_and_auth_token',
]


def find_gacha_url() -> str:
    path = get_cache_path()
    if path is None or not path.exists():
        raise LogNotFoundError('Honkai: Star Rail is not installed or has not been started yet, or the cache file could not be copied.')

    with path.open('rb') as fp:
        cache_file = fp.read()

    regex = re.compile(rb'https://[^\0]+/getGachaLog[^\0]*')
    matches = regex.findall(cache_file)

    logging.debug('Found %d matches for getGachaLog URLs', len(matches))
    if not matches:
        raise AuthTokenExtractionError('Could not find authentication token in the log file. Open the warp history in the game, then try again.')
    return matches[-1].decode('utf-8')


def extract_region_and_auth_token(url: str) -> tuple[str, str]:
    try:
        parsed_url = urlparse(url)
    except ValueError:
        raise AuthTokenExtractionError('Error parsing URL.')

    query_params = parse_qs(parsed_url.query)
    if 'authkey' not in query_params:
        raise AuthTokenExtractionError('Parameter "authkey" missing from URL.')
    if 'game_biz' not in query_params:
        raise AuthTokenExtractionError('Parameter "game_biz" missing from URL.')

    return (query_params['game_biz'][0], query_params['authkey'][0])


def extract_api_endpoint(url: str) -> str:
    try:
        parsed_url = urlparse(url)
    except ValueError:
        raise AuthTokenExtractionError('Error parsing URL.')

    return '{}://{}{}'.format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)
