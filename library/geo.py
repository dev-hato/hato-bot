# coding: utf-8

"""
amesh
"""

import json
import re
from typing import Dict, Optional

import requests
import slackbot_settings as conf


def get_geo_data(place: str) -> Optional[Dict[str, str]]:
    """
    地名や住所から座標を取得する
    :param place: 地名・住所・郵便番号
    :return: place: 地名, lat: 緯度, lon: 経度
    """
    is_zip_code = re.match(r"[0-9]{3}-[0-9]{4}", place)

    if is_zip_code:
        url = "https://map.yahooapis.jp/search/zip/V1/zipCodeSearch"
    else:
        url = "https://map.yahooapis.jp/geocode/V1/geoCoder"

    res = requests.get(
        url, {"appid": conf.YAHOO_API_TOKEN, "query": place, "output": "json"}
    )
    if res.status_code == 200:
        geo_data = json.loads(res.content)
        if "Feature" in geo_data:
            for feature in geo_data["Feature"]:
                if "Geometry" in feature and feature["Geometry"]:
                    geometry = feature["Geometry"]
                    res_place = None

                    if (
                        is_zip_code
                        and "Property" in feature
                        and "Address" in feature["Property"]
                        and feature["Property"]["Address"]
                    ):
                        res_place = feature["Property"]["Address"]
                    elif not is_zip_code and "Name" in feature and feature["Name"]:
                        res_place = feature["Name"]
                    else:
                        return None

                    if "Coordinates" in geometry and geometry["Coordinates"]:
                        coordinates = geometry["Coordinates"]
                        lon, lat = coordinates.split(",", maxsplit=2)
                        return {"place": res_place, "lat": lat, "lon": lon}

    return None
