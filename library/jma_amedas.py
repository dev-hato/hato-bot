import datetime
import math
from typing import Dict, Optional

import requests


def get_jma_amedas(lat: float, lon: float) -> Optional[Dict]:
    nearest_place: Dict[str, int | float | str] = {}
    place_res = requests.get(
        "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"
    )

    if place_res.status_code != 200:
        return None

    for code, place in place_res.json().items():
        decimal_lat = place["lat"][0] + float(place["lat"][1]) / 60
        decimal_lon = place["lon"][0] + float(place["lon"][1]) / 60
        distance = math.sqrt((decimal_lat - lat) ** 2 + (decimal_lon - lon) ** 2)
        if "distance" not in nearest_place or distance < nearest_place["distance"]:
            nearest_place = {
                "code": code,
                "distance": distance,
                "place": place["kjName"],
            }

    latest_datetime_res = requests.get(
        "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
    )

    if latest_datetime_res.status_code != 200:
        return None

    latest_datetime = datetime.datetime.fromisoformat(latest_datetime_res.text)
    amedas_url = latest_datetime.strftime(
        "https://www.jma.go.jp/bosai/amedas/data/map/%Y%m%d%H%M%S.json"
    )
    amedas_res = requests.get(amedas_url)

    if amedas_res.status_code != 200:
        return None

    amedas_data: Dict = amedas_res.json()

    if nearest_place["code"] not in amedas_data:
        return None

    amedas = amedas_data[nearest_place["code"]]
    amedas["place"] = nearest_place["kjName"]
    amedas["datetime"] = latest_datetime.strftime("%Y/%m/%d %H:%M:%S")
    return amedas
