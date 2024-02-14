# coding: utf-8

"""
amesh
"""

import re
import unicodedata
from random import choice
from typing import Dict, Optional

import requests

import slackbot_settings as conf


def get_geo_data(place: str) -> Optional[Dict[str, str]]:
    """
    地名や住所から座標を取得する(ラッパー)
    :param place: 地名・住所・郵便番号
    :return: place: 地名, lat: 緯度, lon: 経度
    """

    geo_data = get_yahoo_geo_data(place)
    if geo_data is not None:
        return geo_data

    return get_gsi_geo_data(place)


def get_yahoo_geo_data(place: str) -> Optional[Dict[str, str]]:
    """
    地名や住所から座標を取得する(Yahoo!地図版)
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

    if res.status_code != 200:
        return None

    for feature in res.json().get("Feature", []):
        coordinates = feature.get("Geometry", {}).get("Coordinates")
        if coordinates is None:
            continue

        res_place = None
        address = feature.get("Property", {}).get("Address")
        name = feature.get("Name")

        if is_zip_code and address is not None:
            res_place = address
        elif not is_zip_code and name is not None:
            res_place = name
        else:
            return None

        lon, lat = coordinates.split(",", maxsplit=2)
        return {"place": res_place, "lat": lat, "lon": lon}

    return None


def get_gsi_geo_data(place: str) -> Optional[Dict[str, str]]:
    """
    地名から座標を取得する(国土地理院版)
    場所名が完全一致で優先して返し、部分一致のうちランダム返すことでそれっぽい挙動にしている
    :param place: 地名・住所
    :return: place: 地名, lat: 緯度, lon: 経度
    """

    place = unicodedata.normalize("NFKC", place)
    res = requests.get(
        "https://msearch.gsi.go.jp/address-search/AddressSearch", {"q": place}
    )

    if res.status_code != 200:
        return None

    exactly_match_candidates = []
    partial_match_candidates = []

    for entry in res.json():
        res_place = unicodedata.normalize(
            "NFKC", entry.get("properties", {}).get("title", "")
        )
        lon, lat = entry.get("geometry", {}).get("coordinates", [None, None])
        if lon is None or lat is None:
            continue

        data = {"place": res_place, "lat": str(lat), "lon": str(lon)}

        if place == res_place:
            exactly_match_candidates.append(data)
        elif place in res_place:
            partial_match_candidates.append(data)

    for candidates in [exactly_match_candidates, partial_match_candidates]:
        if candidates:
            return choice(candidates)

    return None
