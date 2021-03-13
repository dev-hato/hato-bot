# coding: utf-8

"""
jma_amesh
"""

import json
from typing import Optional, Dict, List
from dataclasses import dataclass
from io import BytesIO
from PIL import Image, ImageOps
import requests
import math
import threading
import random

# import slackbot_settings as conf

@dataclass
class GsiTile:
    x: int = 0
    y: int = 0
    zoom_level: int = 10

@dataclass
class GeoCoordRectangle:
    lat_north: float = 0.0
    lat_south: float = 0.0
    lng_east:  float = 0.0
    lng_west:  float = 0.0

@dataclass
class TimeJsonElement:
    basetime: str
    validtime: str
    elements: List[str]

def geocoord2webcoord(lat: float, lng: float, zoom: int) -> [float, float]:
    return [
        (1 << zoom) * ( .5 - math.log(math.tan(math.pi/4 + lat*math.pi/180/2)) / (2*math.pi)),
        (1 << zoom) * (lng + 180) / 360
    ]

def geocoord2tile(lat: float, lng: float, zoom: int) -> GsiTile: 
    centre_webcoord = geocoord2webcoord(lat, lng, zoom)
    return GsiTile(x=int(centre_webcoord[1]), y=int(centre_webcoord[0]), zoom_level=zoom)

def geocoord2tiles(lat: float, lng: float, zoom: int, around_tiles: int) -> List[GsiTile]:
    res = []
    centre_tile = geocoord2tile(lat=lat, lng=lng, zoom=zoom)

    tile_max = 1 << zoom
    for i in range(-around_tiles, around_tiles + 1):
        for j in range(-around_tiles, around_tiles + 1):
            x = centre_tile.x + i
            y = centre_tile.y + j
            if 0 <= x and x < tile_max and 0 <= y and y < tile_max:
                res.append(GsiTile(x=x, y=y, zoom_level=zoom))
    return res

def get_timejson() -> Optional[List[TimeJsonElement]]:
    url = 'https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = [TimeJsonElement(**i) for i in json.loads(response.text)]
        return data
    return None

def get_latest_jma_image(lat: float, lng: float, zoom: int, around_tiles: int) -> Image:
    latest_time = max([i.basetime for i in get_timejson() if i.basetime==i.validtime])
    urls = []
    for tile in geocoord2tiles(lat=lat, lng=lng, around_tiles=around_tiles, zoom=zoom):
        urls.append(f'https://www.jma.go.jp/bosai/jmatile/data/nowc/{latest_time}/none/{latest_time}/surf/hrpns/{zoom}/{tile.x}/{tile.y}.png')
    res = []
    for url in urls:
        res.append(Image.open(BytesIO(requests.get(url).content)))
    dst_image = Image.new('RGBA', (256 * (2*around_tiles+1), 256 * (2*around_tiles+1)))
    for idx, elem in enumerate(res):
        dst_image.paste(elem, (256 * (idx // (around_tiles*2+1)), 256 * (idx % (around_tiles*2+1))))
    dst_image.save('a.png')
    return dst_image

def get_osm_image(lat: float, lng: float, zoom: int, around_tiles: int) -> Image:
    latest_time = max([i.basetime for i in get_timejson() if i.basetime==i.validtime])
    urls = []
    for tile in geocoord2tiles(lat=lat, lng=lng, around_tiles=around_tiles, zoom=zoom):
        s = random.choice(['a','b','c'])
        urls.append(f'https://{s}.tile.openstreetmap.org/{zoom}/{tile.x}/{tile.y}.png')
    res = []
    for url in urls:
        res.append(Image.open(BytesIO(requests.get(url).content)))
    dst_image = Image.new('RGBA', (256 * (2*around_tiles+1), 256 * (2*around_tiles+1)))
    for idx, elem in enumerate(res):
        dst_image.paste(elem, (256 * (idx // (around_tiles*2+1)), 256 * (idx % (around_tiles*2+1))))
    dst_image.save('b.png')
    return dst_image
    
def get_latest_jma_image_with_map(lat: float, lng: float, zoom: int, around_tiles: int) -> Image:
    jma_image = get_latest_jma_image(lat=lat, lng=lng, zoom=zoom, around_tiles=around_tiles)
    alpha255 = jma_image.copy()
    alpha255.putalpha(0)
    jma_image_mask = jma_image.copy().getchannel('A')
    jma_image_mask.save('e.png')
    jma_image.save('f.png')
    jma_image.putalpha(128)
    # jma_image.composite(jma_image_mask)
    jma_image.save('d.png')
    jma_image_trans = Image.composite(jma_image, alpha255, jma_image_mask)
    jma_image_trans.save('g.png')
    osm_image = get_osm_image(lat=lat, lng=lng, zoom=zoom, around_tiles=around_tiles)
    res = Image.alpha_composite(osm_image, jma_image_trans)
    res.save('c.png')

print(max([i.basetime for i in get_timejson()]))
print(get_latest_jma_image_with_map(lat=35.5, lng=139.5, zoom=9, around_tiles=1))
print(get_osm_image(lat=35.5, lng=139.5, zoom=9, around_tiles=1))
print(get_latest_jma_image(lat=35.5, lng=139.5, zoom=9, around_tiles=1))