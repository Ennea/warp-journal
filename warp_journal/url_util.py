from __future__ import annotations

import logging
import re
from typing import NamedTuple
from urllib.parse import ParseResult, urlencode, urlparse, parse_qs

from .paths import get_cache_path
from .exceptions import AuthTokenExtractionError, LogNotFoundError

__all__ = [
    'find_gacha_url',
]


class GachaUrl(NamedTuple):
    parsed_url: ParseResult
    query_dict: dict[str, str]

    @classmethod
    def of(cls, url: str) -> GachaUrl:
        parsed_url = urlparse(url)
        query_multidict = parse_qs(parsed_url.query)
        # There is no method to do the reverse operation,
        # so we convert it into what urlencode accepts
        # (which is more usable anyway).
        query_dict = {k: v[0] for k, v in query_multidict.items()}
        return cls(parsed_url, query_dict)

    @property
    def region(self) -> str | None:
        return self.query_dict.get('game_biz')

    @property
    def auth_token(self) -> str | None:
        return self.query_dict.get('authkey')

    @property
    def url(self) -> str:
        return self.parsed_url.geturl()

    def _with_query(self, query_dict: dict[str, str]) -> GachaUrl:
        parsed_url = self.parsed_url._replace(query=urlencode(query_dict))
        return GachaUrl(parsed_url, query_dict)


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
    url = GachaUrl.of(matches[-1].decode('utf-8'))
    if not url.auth_token:
        raise AuthTokenExtractionError('Parameter "authkey" missing from URL.')
    if not url.region:
        raise AuthTokenExtractionError('Parameter "game_biz" missing from URL.')
    logging.debug('Extracted region and token: %s; %s', url.region, url.auth_token)
    return url
