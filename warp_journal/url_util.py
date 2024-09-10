from __future__ import annotations

import logging
import re
from typing import NamedTuple
from urllib.parse import urlparse, parse_qs

from .paths import get_cache_path
from .exceptions import AuthTokenExtractionError, LogNotFoundError

__all__ = [
    'find_gacha_url',
]


class GachaUrl(NamedTuple):
    url: str
    region: str
    auth_token: str

    @classmethod
    def of(cls, url: str) -> GachaUrl:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'authkey' not in query_params:
            raise AuthTokenExtractionError('Parameter "authkey" missing from URL.')
        if 'game_biz' not in query_params:
            raise AuthTokenExtractionError('Parameter "game_biz" missing from URL.')
        region = query_params['game_biz'][0]
        auth_token = query_params['authkey'][0]
        logging.debug('Extracted region and token: %s; %s', region, auth_token)

        return cls(url, region, auth_token)


def find_gacha_url() -> GachaUrl:
    """Find the URL used to fetch gacha history.

    Raises:
        LogNotFoundError when the log file could not be found.

        AuthTokenExtractionError when a valid URL could not be found.
    """
    path = get_cache_path()
    if path is None or not path.exists():
        raise LogNotFoundError('Honkai: Star Rail is not installed or has not been started yet, or the cache file could not be copied.')

    with path.open('rb') as fp:
        cache_file = fp.read()

    regex = re.compile(rb'https://[^\0]+/getGachaLog[^\0]*')
    matches = regex.findall(cache_file)
    if not matches:
        raise AuthTokenExtractionError('Could not find authentication token in the log file. Open the warp history in the game, then try again.')

    logging.debug('Found %d matches for getGachaLog URLs; using last', len(matches))
    return GachaUrl.of(matches[-1].decode('utf-8'))
