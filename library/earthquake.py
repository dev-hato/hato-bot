# coding: utf-8

"""
地震情報
"""

import json
from typing import Any, List, Optional

import requests
from PIL import Image

from library.hatomap import (
    GeoCoord,
    HatoMap,
    Layer,
    LineTrace,
    MapBox,
    MarkerTrace,
    get_circle,
)


def get_quake_list(limit: int = 10) -> Optional[Any]:
    """
    地震リストを取得
    """
    # 551は地震情報
    # https://www.p2pquake.net/json_api_v2/#/P2P%E5%9C%B0%E9%9C%87%E6%83%85%E5%A0%B1%20API/get_history
    quake_url = f"https://api.p2pquake.net/v2/history?codes=551&limit={limit}"
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
    magnitude: float,
    earthquake_intensity: str,
) -> Image.Image:
    """
    OpenStreetMap画像を取得してMap画像を組み立てる
    Usage: generate_map_img(lat=37, lng=139, zoom=8, around_tiles=2, time="2022/11/15 10:55:00",
                            hypocenter="石川県能登地方", magnitude=4.2, earthquake_intensity="4.0").save('res2.png')
    """

    layers: List[Layer] = [
        LineTrace(coords=[get_circle(lat, lng, d * 1000)], color=(100, 100, 100, 255))
        for d in range(10, 60, 10)
    ]
    layers.append(
        MarkerTrace(
            coords=[GeoCoord(lat, lng)],
            size=14,
            border_color=(0, 0, 255, 255),
            fill_color=(0, 0, 255, 255),
        )
    )
    h = HatoMap(
        basemap="open-street-map-dim",
        title=f"地震 (発生時刻: {time}, 震源地: {hypocenter}, マグニチュード: {magnitude}, 最大震度: {earthquake_intensity})",
        mapbox=MapBox(center=GeoCoord(lat, lng), zoom=zoom),
        layers=layers,
    )
    width = (2 * around_tiles + 1) * 256
    i = h.get_image(width=width, height=width)
    return Image.fromarray(i[:, :, ::-1])  # OpenCV形式からPIL形式に変換
