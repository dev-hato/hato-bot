# coding: utf-8

"""
amesh
"""

import json
import re
from typing import Optional, Dict

import requests

import slackbot_settings as conf


def get_geo_data(place: str) -> Optional[Dict[str, str]]:
    """
    地名や住所から座標を取得する
    :param place: 地名・住所
    :return: place: 地名, lat: 緯度, lon: 経度
    """
    if re.match(r'[0-9]{3}-[0-9]{4}', place):
        url = 'https://map.yahooapis.jp/search/zip/V1/zipCodeSearch'
    else:
        url = 'https://map.yahooapis.jp/geocode/V1/geoCoder'

    res = requests.get(url,
                       {
                           'appid': conf.YAHOO_API_TOKEN,
                           'query': place,
                           'output': 'json'
                       })
    if res.status_code == 200:
        geo_data = json.loads(res.content)
        if 'Feature' in geo_data:
            for feature in geo_data['Feature']:
                if 'Name' in feature and feature['Name'] \
                        and 'Geometry' in feature and feature['Geometry']:
                    geometry = feature['Geometry']
                    if 'Coordinates' in geometry and geometry['Coordinates']:
                        coordinates = geometry['Coordinates']
                        lon, lat = coordinates.split(',', maxsplit=2)
                        return {'place': feature['Name'], 'lat': lat, 'lon': lon}

    return None
