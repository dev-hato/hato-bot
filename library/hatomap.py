from __future__ import annotations

import math
import random
import string
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from multiprocessing import Pool
from typing import List, Optional, Tuple

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

from slackbot_settings import VERSION


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
            256
            * (1 << zoom)
            * (
                0.5
                - math.log(math.tan(math.pi / 4 + geocoord.lat * math.pi / 180 / 2))
                / (2 * math.pi)
            ),
            zoom,
        )

    def to_geocoord(self) -> GeoCoord:
        lng = (360 * self.pixel_x) / (1 << self.zoom_level * 256) - 180
        lat = (
            math.asin(
                math.tanh(
                    math.pi * (1 - 2 * self.pixel_y / (1 << self.zoom_level * 256))
                )
            )
            * 180
            / math.pi
        )
        return GeoCoord(lat, lng)

    def belongs_tile(self) -> WebMercatorTilePixel:
        return WebMercatorTilePixel(
            WebMercatorTile(
                tile_x=int(self.pixel_x // 256),
                tile_y=int(self.pixel_y // 256),
                zoom_level=self.zoom_level,
            ),
            int(round(self.pixel_x % 256)),
            int(round(self.pixel_y % 256)),
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
            ).belongs_tile(),
        )

    def geocoord2pixel(self, geocoord: GeoCoord) -> Tuple[int, int]:
        wmp_coord = WebMercatorPixelCoord.from_geocoord(geocoord, self.zoom)
        return (
            int(round(wmp_coord.pixel_x - self.pixel_x_west)),
            int(round(wmp_coord.pixel_y - self.pixel_y_north)),
        )

    def geocoords2pixel_ndarray(self, geocoords: np.ndarray) -> np.ndarray:
        return (
            np.array(
                [
                    256 * (1 << self.zoom) * (geocoords[..., 1] + 180) / 360
                    - self.pixel_x_west,
                    256
                    * (1 << self.zoom)
                    * (
                        0.5
                        - np.log(
                            np.tan(np.pi / 4 + geocoords[..., 0] * np.pi / 180 / 2)
                        )
                        / (2 * np.pi)
                    )
                    - self.pixel_y_north,
                ]
            )
            .astype(np.int32)
            .T
        )

    def geocoords2pixel_list_ndarray(
        self,
        geocoords: List[np.ndarray],
    ) -> List[np.ndarray]:
        return [self.geocoords2pixel_ndarray(g) for g in geocoords]


@dataclass
class MapBox:
    center: GeoCoord = field(default_factory=lambda: GeoCoord(5, 40))
    zoom: int = 3
    width: int = 800
    height: int = 800

    def pixelbbox(self) -> WebMercatorPixelBBox:
        center_pixel = WebMercatorPixelCoord.from_geocoord(self.center, self.zoom)
        origin_pixel_x = int(round(center_pixel.pixel_x - self.width / 2))
        origin_pixel_y = int(round(center_pixel.pixel_y - self.height / 2))
        return WebMercatorPixelBBox(
            pixel_x_west=origin_pixel_x,
            pixel_x_east=origin_pixel_x + self.width,
            pixel_y_north=origin_pixel_y,
            pixel_y_south=origin_pixel_y + self.height,
            zoom=self.zoom,
        )


@dataclass
class RasterTileServer:
    url: str

    @staticmethod
    def _get_image_content(url):
        return cv2.imdecode(
            np.asarray(
                bytearray(
                    requests.get(
                        url, headers={"user-agent": f"hato-bot/{VERSION}"}
                    ).content
                ),
                dtype=np.uint8,
            ),
            -1,
        )

    def request(self, bbox: WebMercatorPixelBBox) -> np.ndarray:
        (tl_tilepx, rb_tilepx) = bbox.covered_tiles()

        request_urls = []
        for x in range(tl_tilepx.tile.tile_x, rb_tilepx.tile.tile_x + 1):
            for y in range(tl_tilepx.tile.tile_y, rb_tilepx.tile.tile_y + 1):
                request_urls.append(
                    string.Template(self.url).safe_substitute(
                        {"x": x, "y": y, "z": bbox.zoom}
                    )
                )
        with Pool(16) as p:
            imgs = list(p.imap(self._get_image_content, request_urls))

        tile_width_cnt = rb_tilepx.tile.tile_x + 1 - tl_tilepx.tile.tile_x
        tile_height_cnt = rb_tilepx.tile.tile_y + 1 - tl_tilepx.tile.tile_y

        concated = np.concatenate(
            [
                np.concatenate(imgs[i : i + tile_height_cnt], axis=0)
                for i in range(0, len(imgs), tile_height_cnt)
            ],
            axis=1,
        )

        px_top = tl_tilepx.tile_pixel_y
        px_bottom = (tile_height_cnt - 1) * 256 + rb_tilepx.tile_pixel_y
        px_left = tl_tilepx.tile_pixel_x
        px_right = (tile_width_cnt - 1) * 256 + rb_tilepx.tile_pixel_x
        trim = concated[px_top:px_bottom, px_left:px_right]
        return trim


@dataclass
class Layer(metaclass=ABCMeta):

    @abstractmethod
    def get_image(self, bbox: WebMercatorPixelBBox) -> np.ndarray:
        pass


@dataclass
class LineTrace(Layer):
    coords: List["np.ndarray"]
    width: int = 1
    color: Tuple[int, int, int, int] = (255, 0, 255, 255)

    def get_image(self, bbox: WebMercatorPixelBBox) -> np.ndarray:
        img = np.zeros((bbox.height, bbox.width, 4), np.uint8)
        coords = self.coords

        px_coords = bbox.geocoords2pixel_list_ndarray(coords)
        cv2.polylines(
            img,
            px_coords,
            color=self.color,
            thickness=self.width,
            isClosed=True,
            lineType=cv2.LINE_AA,
        )
        return img


@dataclass
class MarkerTrace(Layer):
    coords: List[GeoCoord]
    symbol: str = "circle"
    size: int = 4
    border_color: Tuple[int, int, int, int] = (255, 0, 255, 255)
    border_width: int = 1
    fill_color: Optional[Tuple[int, int, int, int]] = None

    def get_image(self, bbox: WebMercatorPixelBBox) -> np.ndarray:
        img = np.zeros((bbox.height, bbox.width, 4), np.uint8)
        if len(self.coords) == 0:
            return img
        else:
            coords = np.array([[g.lat, g.lng] for g in self.coords])

        px_coords = bbox.geocoords2pixel_ndarray(coords)

        symbols = {
            "thunder": np.array(
                [[1, -3], [-0, -0.5], [2, -0.5], [-1, 3], [0, 0.5], [-2, 0.5]]
            )
            / 6
        }
        if self.symbol == "circle":
            for c in px_coords:
                print(c)
                if self.fill_color is not None:
                    cv2.circle(
                        img,
                        c,
                        int(round(self.size / 2)),
                        thickness=-1,
                        color=self.fill_color,
                        lineType=cv2.LINE_AA,
                    )
                cv2.circle(
                    img,
                    c,
                    int(round(self.size / 2)),
                    thickness=self.border_width,
                    color=self.border_color,
                    lineType=cv2.LINE_AA,
                )
        elif self.symbol == "square":
            for c in px_coords:
                tl = (c - self.size / 2).astype(np.int32)
                br = (c + self.size / 2).astype(np.int32)
                if self.fill_color is not None:
                    cv2.rectangle(
                        img,
                        tl,
                        br,
                        thickness=-1,
                        color=self.fill_color,
                        lineType=cv2.LINE_AA,
                    )
                cv2.rectangle(
                    img,
                    tl,
                    br,
                    thickness=self.border_width,
                    color=self.border_color,
                    lineType=cv2.LINE_AA,
                )
        elif self.symbol in symbols.keys():
            symbol_coords = symbols[self.symbol]
            px_coords = (
                np.repeat(px_coords[:, np.newaxis, :], symbol_coords.shape[0], axis=1)
                + symbol_coords * self.size
            )
            px_coords = px_coords.astype(np.int32)
            for c in px_coords:
                if self.fill_color is not None:
                    cv2.fillPoly(img, [c], color=self.fill_color, lineType=cv2.LINE_AA)
                cv2.polylines(
                    img,
                    [c],
                    color=self.border_color,
                    thickness=self.border_width,
                    isClosed=True,
                    lineType=cv2.LINE_AA,
                )

        return img


@dataclass
class RasterLayer(Layer):
    url: Optional[str] = None
    url_list: Optional[List[str]] = None
    opacity: np.float32 = np.float32(1.0)
    brightness: np.float32 = np.float32(1.0)
    chroma: np.float32 = np.float32(1.0)

    def __init__(self, **kwargs):
        self.url = kwargs.get("url", None)
        self.url_list = kwargs.get("url_list", None)
        self.opacity = np.float32(kwargs.get("opacity", 1.0))
        self.brightness = np.float32(kwargs.get("brightness", 1.0))
        self.chroma = np.float32(kwargs.get("chroma", 1.0))

    def __post_init__(self):
        if not (0 <= self.opacity <= 1.0):
            raise ValueError("Opacity is out of range.")

    def get_image(self, bbox: WebMercatorPixelBBox) -> np.ndarray:
        if self.url_list is not None:
            url = random.choice(self.url_list)
        elif self.url is not None:
            url = self.url
        else:
            raise ValueError("You should give url_list or url")
        layer_img = np.array(RasterTileServer(url).request(bbox), dtype=np.float32)

        if self.brightness != 1.0 or self.chroma != 1.0:
            img_hsv = np.array(
                cv2.cvtColor(layer_img, cv2.COLOR_BGR2HSV), dtype=np.float32
            )
            img_hsv[..., 1] = img_hsv[..., 1] * self.brightness
            img_hsv[..., 2] = img_hsv[..., 2] * self.chroma
            layer_img = np.array(
                cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR), dtype=np.float32
            )

        if self.opacity != 1.0:
            layer_img[layer_img[..., 3] != 0, 3] = int(round(self.opacity * 256))

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
    _, _, w, h = draw.textbbox((0, 0), text, font=fontPIL)
    draw.text(xy=(x, y - h), text=text, fill=color, font=fontPIL)
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

    mapbox: MapBox = field(default_factory=MapBox)
    basemap: str = "open-street-map"
    extra_basemap_server: Optional[str] = None
    layers: Optional[List[Layer]] = None
    title: Optional[str] = None

    def update_layout(
        self, mapbox: Optional[MapBox] = None, layers: Optional[List[Layer]] = None
    ) -> None:
        if mapbox is not None:
            self.mapbox = mapbox
        if layers is not None:
            self.layers = layers

    @property
    def basemap_layer(self):
        basemaps = {
            "open-street-map": RasterLayer(
                url_list=[
                    "https://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
                    "https://b.tile.openstreetmap.org/${z}/${x}/${y}.png",
                    "https://c.tile.openstreetmap.org/${z}/${x}/${y}.png",
                ]
            ),
            "open-street-map-dim": RasterLayer(
                url_list=[
                    "https://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
                    "https://b.tile.openstreetmap.org/${z}/${x}/${y}.png",
                    "https://c.tile.openstreetmap.org/${z}/${x}/${y}.png",
                ],
                brightness=0.8,
                chroma=0.6,
            ),
            "carto-light": RasterLayer(
                url_list=[
                    "https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/${z}/${x}/${y}.png",
                    "https://cartodb-basemaps-c.global.ssl.fastly.net/light_all/${z}/${x}/${y}.png",
                ]
            ),
            "carto-dark": RasterLayer(
                url_list=[
                    "https://cartodb-basemaps-b.global.ssl.fastly.net/dark_all/${z}/${x}/${y}.png",
                    "https://cartodb-basemaps-d.global.ssl.fastly.net/dark_all/${z}/${x}/${y}.png",
                ]
            ),
            "extra": RasterLayer(url_list=[self.extra_basemap_server]),
        }

        if self.basemap in basemaps.keys():
            return basemaps[self.basemap]

        return basemaps["open-street-map"]

    def get_image(self, height: int, width: int) -> np.ndarray:
        offset_top = 0
        if self.title is not None:
            offset_top = 16

        self.mapbox.height = height - offset_top
        self.mapbox.width = width
        none_body_img_shape = (0, 0, 0)
        body_img = np.zeros(none_body_img_shape)
        layers = [self.basemap_layer]

        if self.layers is not None:
            layers += self.layers

        for layer in layers:
            layer_img = layer.get_image(self.mapbox.pixelbbox())
            if body_img.shape == none_body_img_shape:
                body_img = layer_img[..., :3]
            else:
                body_img = body_img[..., :3] * (
                    1 - layer_img[..., 3:] / 255
                ) + layer_img[..., :3] * (layer_img[..., 3:] / 255)

        img = np.zeros((height, width, 3), np.uint8)
        img.fill(255)
        img[offset_top:, :] = body_img
        img = cv2_putText_3(
            img,
            self.title,
            (0, offset_top),
            "./library/assets/ipag.ttf",
            fontScale=16,
            color=(0, 0, 0),
        )

        return img


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
