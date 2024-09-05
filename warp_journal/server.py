import logging
from typing import Optional, cast
import webbrowser
from collections import defaultdict
from copy import deepcopy
import os
from pathlib import Path

import bottle
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

from . import url_util
from .client import Client
from .enums import ItemType
from .exceptions import AuthTokenExtractionError, MissingAuthTokenError, LogNotFoundError, RequestError, EndpointError, UnsupportedRegion


class Server:
    def __init__(self, port):
        self._client = Client()
        self._app = bottle.Bottle()
        self._frontend_path = Path(__file__).parent / 'frontend'

        self._app.route('/', callback=self._index)
        self._app.route('/static/<filename>.js', callback=self._static_files_javascript)
        self._app.route('/static/<filename>', callback=self._static_files)
        self._app.route('/ws', callback=self._websocket)
        self._app.route('/warp-journal', callback=self._identify)
        self._app.route('/data', callback=self._get_data)
        self._app.route('/update-warp-history', method='POST', callback=self._update_warp_history)
        self._app.route('/find-warp-history-url', method='POST', callback=self._find_warp_history_url)

        self._server = WSGIServer(('localhost', port), self._app, handler_class=WebSocketHandler)
        webbrowser.open(f'http://localhost:{port}')
        self._server.serve_forever()

    def _static_file(self, *args, **kwargs):
        response = bottle.static_file(*args, **kwargs, root=self._frontend_path)
        response.set_header('Cache-Control', 'no-store')
        return response

    def _index(self):
        return self._static_file('index.html')

    def _static_files(self, filename):
        return self._static_file(filename)

    def _static_files_javascript(self, filename):
        return self._static_file(filename + '.js', mimetype='text/javascript')

    # a websocket connection that is used to check whether the browser tab is still open
    def _websocket(self):
        ws = bottle.request.environ.get('wsgi.websocket')
        if not ws:
            bottle.abort(400)

        while True:
            try:
                ws.receive()
            except WebSocketError:
                # allow skipping automatic exit when developing on frontend
                if not os.environ.get('DEVEL'):
                    self._server.stop()
                break

    # a simple 204 on a fixed endpoint name; used to identify ourselves to check if
    # there's already an instance of warp journal running when we start it
    def _identify(self):
        bottle.response.status = 204

    # calculate stats and pity. also returns pity the
    # given warp/reward was obtained at, if applicable
    def _calculate_stats_and_pity(self, warp, stats, pity, low_pity):
        current_pity = None
        banner_type = warp['banner_type']

        # 5 star
        if warp['rarity'] == 5:
            current_pity = pity[banner_type]['pity5'] + 1
            if warp['type'] is ItemType.CHARACTER:
                stats['characters5']['total'] += 1
                stats['characters5']['averagePity'].append(current_pity)
            else:
                stats['lightcones5']['total'] += 1
                stats['lightcones5']['averagePity'].append(current_pity)

            low_pity.append({
                'name': warp['name'],
                'pity': current_pity
            })
            pity[banner_type]['pity5'] = 0
        else:
            pity[banner_type]['pity5'] += 1

        # 4 star
        if warp['rarity'] == 4:
            current_pity = pity[banner_type]['pity4'] + 1
            if warp['type'] is ItemType.CHARACTER:
                stats['characters4']['total'] += 1
                stats['characters4']['averagePity'].append(current_pity)
            else:
                stats['lightcones4']['total'] += 1
                stats['lightcones4']['averagePity'].append(current_pity)

            pity[banner_type]['pity4'] = 0
        else:
            pity[banner_type]['pity4'] += 1

        # 3 star
        if warp['rarity'] == 3:
            stats['lightcones3']['total'] += 1

        return current_pity

    # return all data required by the frontend
    def _get_data(self):
        # banner types
        banner_types = self._client.get_banner_types()

        # pity template
        pity_template = {}
        for key, name in banner_types.items():
            pity_template[key] = {
                'name': name,
                'pity4': 0,
                'pity5': 0
            }

        uids = {}
        for uid in self._client.get_uids():
            uids[uid] = {
                'statistics': {
                    'characters5': { 'total': 0, 'averagePity': [] },
                    'lightcones5': { 'total': 0, 'averagePity': [] },
                    'characters4': { 'total': 0, 'averagePity': [] },
                    'lightcones4': { 'total': 0, 'averagePity': [] },
                    'lightcones3': { 'total': 0 }
                },
                'pity': deepcopy(pity_template),
                'lowPity': [],
                'warpHistory': []
            }

            # shorthands
            data = uids[uid]
            stats = data['statistics']
            pity = data['pity']
            low_pity = data['lowPity']
            warp_history = data['warpHistory']

            for warp in self._client.get_warp_history(uid):
                current_pity = self._calculate_stats_and_pity(warp, stats, pity, low_pity)

                # insert warp copy into frontend-ready history
                warp['type'] = 'Character' if warp['type'] is ItemType.CHARACTER else 'Light Cone'
                warp['bannerType'] = warp['banner_type']
                warp['bannerTypeName'] = banner_types[warp['banner_type']]
                warp['rarityText'] = '✦' * warp['rarity']
                warp['pity'] = current_pity
                del warp['banner_type']
                warp_history.append(warp)

            # calculate average pity
            for _, category in stats.items():
                if 'averagePity' in category:
                    category['averagePity'] = (
                        sum(category['averagePity']) / len(category['averagePity'])
                        if len(category['averagePity']) > 0 else 0
                    )

            # transform pity into a list
            if 2 in pity:
                del pity[2]  # remove beginner warps
            pity = [ banner for _, banner in pity.items() ]

            # sort and clamp low pity
            low_pity.sort(key=lambda reward: reward['pity'])
            data['lowPity'] = low_pity[:5]

            # re-sort the history now that all banner types are merged,
            # replace 'id' with an incremental counter,
            # add a per-banner counter,
            # and then reverse it for display in the frontend
            warp_history.sort(key=lambda warp: warp['id'])
            counts = defaultdict(int)
            for i, warp in enumerate(warp_history):
                warp['id'] = i
                counts[warp['bannerTypeName']] += 1
                warp['numOnBanner'] = counts[warp['bannerTypeName']]
            warp_history.reverse()

            data['totalWarps'] = len(warp_history)
            # uid loop end

        return {
            'bannerTypes': banner_types,
            'uids': uids
        }

    def _update_warp_history(self):
        body = cast(Optional[dict], bottle.request.json)
        url = body.get('url') if body else None
        try:
            if not url:
                url = url_util.find_gacha_url()
            region, auth_token = url_util.extract_region_and_auth_token(url)
            api_endpoint = url_util.extract_api_endpoint(url)
        except (AuthTokenExtractionError, LogNotFoundError) as e:
            bottle.response.status = 400
            logging.warning('Unable to extract auth token: %s', e)
            return {'message': str(e)}

        logging.debug('Extracted region and token: %s; %s', region, auth_token)
        self._client.set_region_and_auth_token(region, auth_token)
        self._client.set_api_endpoint(api_endpoint)
        try:
            new_warps_count = self._client.fetch_and_store_warp_history()
        except (MissingAuthTokenError, RequestError, EndpointError, UnsupportedRegion) as e:
            bottle.response.status = 500
            return {
                'message': str(e)
            }

        return {
            'message': f'Retrieved {new_warps_count} new {"warp" if new_warps_count == 1 else "warps"}.'
        }

    def _find_warp_history_url(self):
        try:
            url = url_util.find_gacha_url()
            url_util.extract_region_and_auth_token(url)
        except (AuthTokenExtractionError, LogNotFoundError) as e:
            bottle.response.status = 400
            logging.warning('Unable to extract auth token: %s', e)
            return {'message': str(e)}

        return {'url': url}
