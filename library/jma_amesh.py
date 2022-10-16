# coding: utf-8

"""
jma_amesh
"""
import datetime
import json
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import requests
from PIL import Image

from library.hatomap import (
    GeoCoord,
    HatoMap,
    LineTrace,
    MapBox,
    MarkerTrace,
    RasterLayer,
)


@dataclass
class WebMercatorTile:
    """Webメルカトル座標上のタイル"""

    tile_x: int = 0
    tile_y: int = 0
    zoom_level: int = 10


@dataclass
class TimeJsonElement:
    """targetTimesの要素"""

    basetime: str
    validtime: str
    elements: List[str]


def get_latest_timestamps() -> dict:
    """データごとの最終更新時刻を取得する"""
    urls = [
        "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json",
        "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N2.json",
        "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N3.json",
    ]
    timejson = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data = [TimeJsonElement(**i) for i in json.loads(response.text)]
            timejson += data

    elements = list(set([e for i in timejson for e in i.elements]))
    return dict(
        [
            (
                e,
                max(
                    [
                        i.basetime
                        for i in timejson
                        if i.basetime == i.validtime and e in i.elements
                    ]
                ),
            )
            for e in elements
        ]
    )


def timestamp2jst(timestamp: str) -> str:
    """targetTimes.jsonの時刻書式をJSTに変換し読みやすくする"""
    return (
        datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        .replace(tzinfo=datetime.timezone.utc)
        .astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        .strftime("%Y-%m-%d %H:%M")
    )


def get_jma_image_server(timestamp: str) -> str:
    """気象庁雨雲レーダー画像を取得する"""
    return f"https://www.jma.go.jp/bosai/jmatile/data/nowc/{timestamp}/none/{timestamp}/surf/hrpns/${{z}}/${{x}}/${{y}}.png"  # noqa: E501


def get_liden(timestamp: str) -> List[Tuple[float, float, int]]:
    """気象庁落雷JSONを取得する"""
    liden_json_url = f"https://www.jma.go.jp/bosai/jmatile/data/nowc/{timestamp}/none/{timestamp}/surf/liden/data.geojson"  # noqa: E501
    response = requests.get(liden_json_url)

    if response.status_code == 200:
        return [
            (
                e["geometry"]["coordinates"][1],
                e["geometry"]["coordinates"][0],
                e["properties"]["type"],
            )
            for e in json.loads(response.text)["features"]
        ]
    return [(0.0, 0.0, 0)]


def get_circle(lat: float, lng: float, radius: float) -> np.ndarray:
    """指定した地点から半径radiusメートルの正360角形の頂点を列挙する"""
    earth_radius = 6378137
    earth_f = 298.257222101
    earth_e_sq = (2 * earth_f - 1) / earth_f**2
    c = 1 - (earth_e_sq * math.sin(lat) ** 2)
    meter_1deg_lat = math.pi * earth_radius * (1 - earth_e_sq) / (180 * c**1.5)
    meter_1deg_lng = (
        math.pi * earth_radius * math.cos(lat * math.pi / 180) / (180 * math.sqrt(c))
    )
    lats = np.sin(np.radians(np.arange(0, 361, 1))) * radius / meter_1deg_lat + lat
    lngs = np.cos(np.radians(np.arange(0, 361, 1))) * radius / meter_1deg_lng + lng
    return np.array([lats, lngs]).T


def jma_amesh(
    lat: float, lng: float, zoom: int, around_tiles: int
) -> Optional[Image.Image]:
    """
    気象庁雨雲レーダーとOpenStreatMap画像を取得して結合する
    Usage: jma_amesh(lat=37, lng=139, zoom=8, around_tiles=2).save('res2.png')
    """

    jma_timestamp = get_latest_timestamps()
    h = HatoMap(
        basemap="open-street-map-dim",
        title=f'雨雲:{timestamp2jst(jma_timestamp["hrpns_nd"])} 雷:{timestamp2jst(jma_timestamp["liden"])}',
        mapbox=MapBox(center=GeoCoord(lat, lng), zoom=zoom),
        layers=[
            RasterLayer(
                url=get_jma_image_server(jma_timestamp["hrpns_nd"]), opacity=128 / 256
            )
        ]
        + [
            LineTrace(
                coords_list_ndarray=[get_circle(lat, lng, d * 1000)], color=(100, 100, 100, 255)
            )
            for d in range(10, 60, 10)
        ]
        + [
            MarkerTrace(
                coords_list_geo_cooord=[GeoCoord(e[0], e[1]) for e in get_liden(jma_timestamp["liden"])],
                size=14,
                symbol="thunder",
                fill_color=(0, 255, 255, 255),
                border_color=(0, 64, 64, 255),
            )
        ],
    )
    width = (2 * around_tiles + 1) * 256
    i = h.get_image(width=width, height=width)
    return Image.fromarray(i[:, :, ::-1])  # OpenCV形式からPIL形式に変換
