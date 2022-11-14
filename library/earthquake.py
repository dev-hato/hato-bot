# coding: utf-8

"""
地震情報
"""

import json
from typing import Any, Optional

import requests
from PIL import Image

from library.hatomap import (
    GeoCoord,
    HatoMap,
    LineTrace,
    MapBox,
    MarkerTrace,
    get_circle,
)


def get_quake_list(limit: int = 10) -> Optional[Any]:
    """
    地震リストを取得
    """
    quake_url = f"https://api.p2pquake.net/v1/human-readable?limit={limit}"
    response = requests.get(quake_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None


def generate_map_img(
    lat: float,
    lng: float,
    zoom: int,
    around_tiles: int,
    time: str,
    hypocenter: str,
    magnitude: str,
    earthquake_intensity: str,
) -> Optional[Image.Image]:
    """
    OpenStreetMap画像を取得してMap画像を組み立てる
    Usage: generate_map_img(lat=37, lng=139, zoom=8, around_tiles=2, time="14日22時28分", hypocenter="石川県能登地方", magnitude="4.2", earthquake_intensity="4.0").save('res2.png')
    """

    h = HatoMap(
        basemap="open-street-map-dim",
        title=f"地震 (発生時刻: {time}, 震源地: {hypocenter}, マグニチュード: {magnitude}, 最大震度: {earthquake_intensity})",
        mapbox=MapBox(center=GeoCoord(lat, lng), zoom=zoom),
        layers=[
            LineTrace(
                coords=[get_circle(lat, lng, d * 1000)], color=(100, 100, 100, 255)
            )
            for d in range(10, 60, 10)
        ]
        + [
            MarkerTrace(
                coords=[GeoCoord(lat, lng)],
                size=14,
                border_color=(0, 0, 255, 255),
                fill_color=(0, 0, 255, 255),
            )
        ],
    )
    width = (2 * around_tiles + 1) * 256
    i = h.get_image(width=width, height=width)
    return Image.fromarray(i[:, :, ::-1])  # OpenCV形式からPIL形式に変換
