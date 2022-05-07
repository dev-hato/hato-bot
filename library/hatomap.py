from __future__ import annotations
from dataclasses import dataclass, field
from multiprocessing import Pool

import string
from typing import Any, List, Literal, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import requests
import cv2
import random


@dataclass
class WebMercatorTile:
    tile_x: int
    tile_y: int
    zoom_level: int


@dataclass
class WebMercatorTilePixel:
    tile: WebMercatorTile
    tile_pixel_x: int
    tile_pixel_y: int


@dataclass
class GeoCoord:
    lat: float
    lng: float

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitude is out of range.")
        if not (-180 <= self.lng <= 180):
            raise ValueError("Longiture is out of range.")


@dataclass
class WebMercatorPixelCoord:
    pixel_x: float
    pixel_y: float
    zoom_level: int

    @classmethod
    def from_geocoord(cls, geocoord: GeoCoord, zoom: int) -> WebMercatorPixelCoord:
        return cls(
            256 * (1 << zoom) * (geocoord.lng + 180) / 360,
            256 * (1 << zoom) * (.5 - math.log(math.tan(math.pi /
                                                        4 + geocoord.lat*math.pi/180/2)) / (2*math.pi)),
            zoom
        )

    def to_geocoord(self) -> GeoCoord:
        lng = (360 * self.pixel_x) / (1 << self.zoom_level * 256) - 180
        lat = math.asin(math.tanh(
            math.pi * (1 - 2 * self.pixel_y / (1 << self.zoom_level * 256)))) * 180 / math.pi
        return GeoCoord(lat, lng)

    def belongs_tile(self) -> WebMercatorTilePixel:
        return WebMercatorTilePixel(
            WebMercatorTile(
                tile_x=self.pixel_x // 256,
                tile_y=self.pixel_y // 256,
                zoom_level=self.zoom_level
            ),
            int(round(self.pixel_x % 256)),
            int(round(self.pixel_y % 256))
        )


@dataclass
class WebMercatorPixelBBox:
    pixel_x_east: int
    pixel_x_west: int
    pixel_y_north: int
    pixel_y_south: int
    zoom: int
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        self.width = self.pixel_x_east - self.pixel_x_west
        self.height = self.pixel_y_south - self.pixel_y_north

    def covered_tiles(self) -> Tuple[WebMercatorTilePixel, WebMercatorTilePixel]:
        return (
            WebMercatorPixelCoord(
                self.pixel_x_west, self.pixel_y_north, self.zoom
            ).belongs_tile(),
            WebMercatorPixelCoord(
                self.pixel_x_east, self.pixel_y_south, self.zoom
            ).belongs_tile()
        )

    def geocoord2pixel(self, geocoord: GeoCoord) -> Tuple(int, int):
        wmp_coord = WebMercatorPixelCoord.from_geocoord(geocoord, self.zoom)
        return (
            int(round(wmp_coord.pixel_x - self.pixel_x_west)),
            int(round(wmp_coord.pixel_y - self.pixel_y_north))
        )

    def _ndarray_geocoords2pixel(self, geocoords: np.ndarray) -> np.ndarray:
        return np.array([
            256 * (1 << self.zoom) *
            (geocoords[..., 1] + 180) / 360 - self.pixel_x_west,
            256 * (1 << self.zoom) * (.5 - np.log(np.tan(np.pi/4 +
                                                         geocoords[..., 0]*np.pi/180/2)) / (2*np.pi)) - self.pixel_y_north
        ]).astype(np.int32).T

    def geocoords2pixel(
            self, geocoords: Union[np.ndarray, List[np.ndarray], List[GeoCoord], List[List[GeoCoord]]]) -> Any:

        if type(geocoords) is np.ndarray:
            return self._ndarray_geocoords2pixel(geocoords)
        if type(geocoords[0]) is np.ndarray:
            return [self._ndarray_geocoords2pixel(g) for g in geocoords]

        if type(geocoords[0]) is GeoCoord:
            return [self.geocoord2pixel(g) for g in geocoords]
        if type(geocoords[0][0]) is GeoCoord:
            return [[self.geocoord2pixel(g) for g in gg] for gg in geocoords]


@dataclass
class MapBox:
    center: GeoCoord = GeoCoord(5, 40)
    zoom: int = 3
    width: int = 800
    height: int = 800

    def pixelbbox(self) -> WebMercatorPixelBBox:
        center_pixel = WebMercatorPixelCoord.from_geocoord(
            self.center, self.zoom)
        origin_pixel_x = int(round(center_pixel.pixel_x - self.width / 2))
        origin_pixel_y = int(round(center_pixel.pixel_y - self.height / 2))
        return WebMercatorPixelBBox(
            pixel_x_west=origin_pixel_x,
            pixel_x_east=origin_pixel_x + self.width,
            pixel_y_north=origin_pixel_y,
            pixel_y_south=origin_pixel_y + self.height,
            zoom=self.zoom
        )


@dataclass
class RasterTileServer:
    url: str

    @staticmethod
    def _get_image_content(url):
        return cv2.imdecode(
            np.asarray(bytearray(requests.get(url).content), dtype=np.uint8),
            -1
        )

    def request(self, bbox: WebMercatorPixelBBox = None) -> np.ndarray:
        if bbox is None or False:
            return None

        (tl_tilepx, rb_tilepx) = bbox.covered_tiles()

        request_urls = []
        for x in range(tl_tilepx.tile.tile_x, rb_tilepx.tile.tile_x+1):
            for y in range(tl_tilepx.tile.tile_y, rb_tilepx.tile.tile_y+1):
                request_urls.append(
                    string.Template(self.url).safe_substitute({
                        "x": x, "y": y, "z": bbox.zoom
                    })
                )
        with Pool(16) as p:
            imgs = list(p.imap(self._get_image_content, request_urls))

        tile_width_cnt = rb_tilepx.tile.tile_x + 1 - tl_tilepx.tile.tile_x
        tile_height_cnt = rb_tilepx.tile.tile_y + 1 - tl_tilepx.tile.tile_y

        concated = np.concatenate(
            [
                np.concatenate(imgs[i:i+tile_height_cnt], axis=0) for i in range(0, len(imgs), tile_height_cnt)
            ],
            axis=1
        )

        px_top = tl_tilepx.tile_pixel_y
        px_bottom = (tile_height_cnt - 1) * 256 + rb_tilepx.tile_pixel_y
        px_left = tl_tilepx.tile_pixel_x
        px_right = (tile_width_cnt - 1) * 256 + rb_tilepx.tile_pixel_x
        trim = concated[px_top:px_bottom, px_left:px_right]
        return trim


@dataclass
class LineTrace:
    coords: Union[List["np.ndarray"], List[List[GeoCoord]]]
    width: int = 1
    color: Tuple(int, int, int, int) = (255, 0, 255, 255)

    def get_image(self, bbox: WebMercatorPixelBBox = None) -> np.ndarray:
        img = np.zeros((bbox.height, bbox.width, 4), np.uint8)
        if type(self.coords[0][0]) is GeoCoord:
            coords = [np.array([[g.lat, g.lng] for g in coords])
                      for coords in self.coords]
        elif type(self.coords[0][0][0]) is np.float64:
            coords = self.coords
        else:
            raise TypeError(
                "coords should be List[np.ndarray] or List[List[GeoCoord]]")

        px_coords = bbox.geocoords2pixel(coords)
        cv2.polylines(img, px_coords, color=self.color,
                      thickness=self.width, isClosed=True, lineType=cv2.LINE_AA)
        return img


@dataclass
class MarkerTrace:
    coords: Union["np.ndarray", List[GeoCoord]]
    symbol: str = "circle"
    size: int = 4
    border_color: Tuple(int, int, int) = (255, 0, 255, 255)
    border_width: int = 1
    fill_color: Optional[Tuple(int, int, int, int)] = None

    def get_image(self, bbox: WebMercatorPixelBBox = None) -> np.ndarray:

        img = np.zeros((bbox.height, bbox.width, 4), np.uint8)
        if len(self.coords) == 0:
            return img
        if type(self.coords[0]) is GeoCoord:
            coords = np.array([[g.lat, g.lng] for g in self.coords])
        elif type(self.coords[0][0]) is np.float64:
            coords = self.coords
        else:
            raise TypeError(
                "coords should be List[np.ndarray] or List[List[GeoCoord]]")

        px_coords = bbox.geocoords2pixel(coords)

        symbols = {
            "thunder": np.array([
                [1, -3], [-0, -0.5], [2, -0.5], [-1, 3], [0, 0.5], [-2, 0.5]
            ]) / 6
        }
        if self.symbol == "circle":
            for c in px_coords:
                print(c)
                if self.fill_color is not None:
                    cv2.circle(img, c, int(round(self.size/2)), thickness=-
                               1, color=self.fill_color, lineType=cv2.LINE_AA)
                cv2.circle(img, c, int(round(self.size/2)), thickness=self.border_width,
                           color=self.border_color, lineType=cv2.LINE_AA)
        elif self.symbol == "square":
            for c in px_coords:
                tl = (c - self.size / 2).astype(np.int32)
                br = (c + self.size / 2).astype(np.int32)
                if self.fill_color is not None:
                    cv2.rectangle(img, tl, br, thickness=-1,
                                  color=self.fill_color, lineType=cv2.LINE_AA)
                cv2.rectangle(img, tl, br, thickness=self.border_width,
                              color=self.border_color, lineType=cv2.LINE_AA)
        elif self.symbol in symbols.keys():
            symbol_coords = symbols[self.symbol]
            px_coords = np.repeat(
                px_coords[:, np.newaxis, :], symbol_coords.shape[0], axis=1
            ) + symbol_coords * self.size
            px_coords = px_coords.astype(np.int32)
            for c in px_coords:
                if self.fill_color is not None:
                    cv2.fillPoly(
                        img, [c], color=self.fill_color, lineType=cv2.LINE_AA)
                cv2.polylines(img, [c], color=self.border_color,
                              thickness=self.border_width, isClosed=True, lineType=cv2.LINE_AA)

        return img


@dataclass
class RasterLayer:
    url: Union[List[str], str]
    opacity: float = 1.0
    brightness: float = 1.0
    chroma: float = 1.0

    def __post_init__(self):
        if not (0 <= self.opacity <= 1.0):
            raise ValueError('Opacity is out of range.')

    def get_image(self, bbox: WebMercatorPixelBBox = None) -> np.ndarray:
        if type(self.url) is list:
            url = random.choice(self.url)
        else:
            url = self.url
        layer_img = RasterTileServer(url).request(bbox)

        if self.brightness != 1.0 or self.chroma != 1.0:
            img_hsv = cv2.cvtColor(layer_img, cv2.COLOR_BGR2HSV)
            img_hsv[..., (1)] = img_hsv[..., (1)] * self.brightness
            img_hsv[..., (2)] = img_hsv[..., (2)] * self.chroma
            layer_img = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)

        if self.opacity != 1.0:
            layer_img[layer_img[..., 3] != 0, 3] = int(
                round(self.opacity * 256))

        return layer_img


def cv2_putText_3(img, text, org, fontFace, fontScale, color):
    """
    OpenCVでも日本語フォントでテキストを挿入する。
    # https://qiita.com/mo256man/items/b6e17b5a66d1ea13b5e3
    """
    x, y = org
    imgPIL = Image.fromarray(img)
    draw = ImageDraw.Draw(imgPIL)
    fontPIL = ImageFont.truetype(font=fontFace, size=fontScale)
    w, h = draw.textsize(text, font=fontPIL)
    draw.text(xy=(x, y-h), text=text, fill=color, font=fontPIL)
    return np.array(imgPIL, dtype=np.uint8)


@dataclass
class HatoMap:
    """
    mapbox: 地図の表示範囲と地図の大きさ
    basemap: 描画する地図の種類（open-street-mapなど）
    extra_basemap_server: 描画する地図をプリセット以外にする
    layers: 地図の上から地図タイルや線・点などを描画する
    title: タイトル
    """
    mapbox: MapBox = MapBox()
    basemap: str = 'open-street-map'
    extra_basemap_server: str = None
    layers: List[Union[RasterLayer, LineTrace]] = None
    title: str = None

    def update_layout(
        self,
        mapbox: MapBox = None,
        layers: List[Union[RasterLayer, LineTrace]] = None
    ) -> None:
        if mapbox is not None:
            self.mapbox = mapbox
        if layers is not None:
            self.layers = layers

    @property
    def basemap_layer(self):
        basemaps = {
            'open-street-map': RasterLayer([
                'https://a.tile.openstreetmap.org/${z}/${x}/${y}.png',
                'https://b.tile.openstreetmap.org/${z}/${x}/${y}.png',
                'https://c.tile.openstreetmap.org/${z}/${x}/${y}.png'
            ]),
            'open-street-map-dim': RasterLayer([
                'https://a.tile.openstreetmap.org/${z}/${x}/${y}.png',
                'https://b.tile.openstreetmap.org/${z}/${x}/${y}.png',
                'https://c.tile.openstreetmap.org/${z}/${x}/${y}.png'
            ],
                brightness=0.8, chroma=0.6
            ),
            'carto-light': RasterLayer([
                'https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/${z}/${x}/${y}.png',
                'https://cartodb-basemaps-c.global.ssl.fastly.net/light_all/${z}/${x}/${y}.png',
            ]),
            'carto-dark': RasterLayer([
                'https://cartodb-basemaps-b.global.ssl.fastly.net/dark_all/${z}/${x}/${y}.png',
                'https://cartodb-basemaps-d.global.ssl.fastly.net/dark_all/${z}/${x}/${y}.png',
            ]),
            'extra': RasterLayer([
                self.extra_basemap_server
            ])
        }

        if self.basemap in basemaps.keys():
            return basemaps[self.basemap]

        return basemaps['open-street-map']

    def get_image(self, height: int = None, width: int = None) -> np.ndarray:
        offset_top = 0
        if self.title is not None:
            offset_top = 16

        if height is not None:
            self.mapbox.height = height - offset_top
        if width is not None:
            self.mapbox.width = width
        body_img = None

        for layer in [self.basemap_layer] + self.layers:
            layer_img = layer.get_image(self.mapbox.pixelbbox())
            if body_img is None:
                body_img = layer_img[..., :3]
            else:
                body_img = body_img[..., :3] * (1-layer_img[..., 3:] / 255) + \
                    layer_img[..., :3] * (layer_img[..., 3:] / 255)

        img = np.zeros((height, width, 3), np.uint8)
        img.fill(255)
        img[offset_top:, :] = body_img
        img = cv2_putText_3(img, self.title, (0, offset_top), "./assets/ipag.ttf",
                            fontScale=16,
                            color=(0, 0, 0))

        return img
