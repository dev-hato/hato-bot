# coding: utf-8

"""
地震情報
"""

import imghdr
import json
import os
from tempfile import NamedTemporaryFile
from typing import Any, Optional

import requests
from PIL import Image

from library.clientclass import BaseClient
from library.hatomap import HatoMap, MapBox, GeoCoord, LineTrace, MarkerTrace, get_circle


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
        lat: float, lng: float, zoom: int, around_tiles: int, cnt: int, time: str, singenti: str, magnitude: str,
        sindo: str
) -> Optional[Image.Image]:
    """
    OpenStreetMap画像を取得してMap画像を組み立てる
    Usage: generate_map_img(lat=37, lng=139, zoom=8, around_tiles=2, cnt=1, time="14日22時28分", singenti="石川県能登地方", magnitude="4.2", sindo="4.0").save('res2.png')
    """

    h = HatoMap(
        basemap="open-street-map-dim",
        title=f'({cnt}) 地震 (発生時刻: {time}, 震源地: {singenti}, マグニチュード: {magnitude}, 最大震度: {sindo})',
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


def generate_quake_info_for_slack(data: Any, client: BaseClient, max_cnt: int = 1) -> str:
    """
    地震情報をslack表示用に加工する
    """
    cnt = 1
    msg: str = "```\n"
    msg += "出典: https://www.p2pquake.net/dev/json-api/ \n"
    msg += "気象庁HP: https://www.jma.go.jp/jp/quake/\n"
    msg += "```"
    client.post(msg)
    for row in data:
        code = int(row["code"])
        if code == 551:  # 551は地震情報 https://www.p2pquake.net/dev/json-api/#i-6
            time = row["earthquake"]["time"]
            singenti = row["earthquake"]["hypocenter"]["name"]
            magnitude = row["earthquake"]["hypocenter"]["magnitude"]
            sindo = row["earthquake"]["maxScale"]

            if sindo is None:
                sindo = ""
            else:
                sindo /= 10
                sindo = str(sindo)

            msg = "```\n"
            msg += f"({cnt})\n"
            msg += f"発生時刻: {time}\n"
            msg += f"震源地: {singenti}\n"
            msg += f"マグニチュード: {magnitude}\n"
            msg += f"最大震度: {sindo}\n"
            msg += "```"
            client.post(msg)

            lat = row["earthquake"]["hypocenter"]["latitude"].replace("N", "")
            lng = row["earthquake"]["hypocenter"]["longitude"].replace("E", "")

            if lat != "" and lng != "":
                map_img = generate_map_img(lat=float(lat), lng=float(lng), zoom=10, around_tiles=2, cnt=cnt, time=time,
                                           singenti=singenti, magnitude=magnitude, sindo=sindo)
                with NamedTemporaryFile() as map_file:
                    map_img.save(map_file, format="PNG")

                    filename = ["map"]
                    ext = imghdr.what(map_file.name)

                    if ext:
                        filename.append(ext)

                    client.upload(
                        file=map_file.name, filename=os.path.extsep.join(filename)
                    )
            if max_cnt <= cnt:
                break
            cnt += 1
    return msg
