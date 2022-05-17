# coding: utf-8

"""
jma_amesh
"""

import json
import math
import random
from dataclasses import dataclass
from io import BytesIO
from string import Template
from typing import List, Optional, Tuple

import requests
from PIL import Image, ImageEnhance


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


def geocoord2webcoord(lat: float, lng: float, zoom: int) -> Tuple[float, float]:
    """緯度，経度をWebメルカトル座標に変換する"""
    return (
        (1 << zoom)
        * (
            0.5
            - math.log(math.tan(math.pi / 4 + lat * math.pi / 180 / 2)) / (2 * math.pi)
        ),
        (1 << zoom) * (lng + 180) / 360,
    )


def geocoord2tile(lat: float, lng: float, zoom: int) -> WebMercatorTile:
    """緯度，経度を含むWebメルカトルタイルに変換する"""
    centre_webcoord = geocoord2webcoord(lat, lng, zoom)
    return WebMercatorTile(
        tile_x=int(centre_webcoord[1]), tile_y=int(centre_webcoord[0]), zoom_level=zoom
    )


def geocoord2tiles(
    lat: float, lng: float, zoom: int, around_tiles: int
) -> List[WebMercatorTile]:
    """緯度，経度を含むWebメルカトルタイル及びその半径aマスのタイルを取得する"""
    res = []
    centre_tile = geocoord2tile(lat=lat, lng=lng, zoom=zoom)

    tile_max = 1 << zoom
    for i in range(-around_tiles, around_tiles + 1):
        for j in range(-around_tiles, around_tiles + 1):
            tile_x = centre_tile.tile_x + i
            tile_y = centre_tile.tile_y + j
            if 0 <= tile_x < tile_max and 0 <= tile_y < tile_max:
                res.append(
                    WebMercatorTile(tile_x=tile_x, tile_y=tile_y, zoom_level=zoom)
                )
    return res


def get_timejson() -> Optional[List[TimeJsonElement]]:
    """有効な時刻を取得する"""
    url = "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = [TimeJsonElement(**i) for i in json.loads(response.text)]
        return data
    return None


def get_tile_image(
    url_template: Template, lat: float, lng: float, zoom: int, around_tiles: int
) -> Image:
    """緯度，経度を含むWebメルカトルタイル及びその半径aマスのタイルを，タイルサーバから画像を取得し結合する"""
    urls = []
    for tile in geocoord2tiles(lat=lat, lng=lng, around_tiles=around_tiles, zoom=zoom):
        urls.append(
            url_template.substitute({"zoom": zoom, "x": tile.tile_x, "y": tile.tile_y})
        )
    res = []
    for url in urls:
        res.append(Image.open(BytesIO(requests.get(url).content)))
    dst_image = Image.new(
        "RGBA", (256 * (2 * around_tiles + 1), 256 * (2 * around_tiles + 1))
    )
    for idx, elem in enumerate(res):
        dst_image.paste(
            elem,
            (
                256 * (idx // (around_tiles * 2 + 1)),
                256 * (idx % (around_tiles * 2 + 1)),
            ),
        )
    return dst_image


def get_latest_jma_image(
    lat: float, lng: float, zoom: int, around_tiles: int
) -> Optional[Image.Image]:
    """気象庁雨雲レーダー画像を取得する"""
    timejson = get_timejson()
    if timejson is None:
        return None
    latest_time = max([i.basetime for i in timejson if i.basetime == i.validtime])

    return get_tile_image(
        url_template=Template(
            # pylint: disable=C0301
            f"https://www.jma.go.jp/bosai/jmatile/data/nowc/{latest_time}/none/{latest_time}/surf/hrpns/${{zoom}}/${{x}}/${{y}}.png"  # noqa: E501
        ),
        lat=lat,
        lng=lng,
        zoom=zoom,
        around_tiles=around_tiles,
    )


def get_osm_image(lat: float, lng: float, zoom: int, around_tiles: int) -> Image:
    """OpenStreatMap画像を取得する"""
    osm_server = random.choice(["a", "b", "c"])
    return get_tile_image(
        url_template=Template(
            f"https://{osm_server}.tile.openstreetmap.org/${{zoom}}/${{x}}/${{y}}.png"
        ),
        lat=lat,
        lng=lng,
        zoom=zoom,
        around_tiles=around_tiles,
    )


def jma_amesh(
    lat: float, lng: float, zoom: int, around_tiles: int
) -> Optional[Image.Image]:
    """
    気象庁雨雲レーダーとOpenStreatMap画像を取得して結合する
    Usage: jma_amesh(lat=37, lng=139, zoom=8, around_tiles=2).save('res2.png')
    """
    jma_image = get_latest_jma_image(
        lat=lat, lng=lng, zoom=zoom, around_tiles=around_tiles
    )
    if jma_image is None:
        return None
    jma_image_alpha = jma_image.copy()
    jma_image_alpha.putalpha(0)
    jma_image_mask = jma_image.copy().getchannel("A")
    jma_image.putalpha(128)
    jma_image_trans = Image.composite(jma_image, jma_image_alpha, jma_image_mask)
    osm_image = get_osm_image(lat=lat, lng=lng, zoom=zoom, around_tiles=around_tiles)
    converter = ImageEnhance.Brightness(osm_image)
    osm_image = converter.enhance(0.6)
    return Image.alpha_composite(osm_image, jma_image_trans)
