"""
amesh.pyのテスト
"""
import json
import unittest

import requests_mock

import slackbot_settings as conf
from library.geo import get_gsi_geo_data, get_yahoo_geo_data


def set_yahoo_mock(
    place: str, mocker: requests_mock.Mocker, is_zip_code: bool, content=None
):
    """
    Mockを設定する
    :param place: 地名・住所・郵便番号
    :param mocker: requestsのMocker
    :param is_zip_code: 郵便番号かどうか
    :param content: req.contentの内容
    """
    if content is None:
        content = {}

    params = {"appid": conf.YAHOO_API_TOKEN, "query": place, "output": "json"}
    query = "&".join([f"{k}={v}" for k, v in params.items()])

    if is_zip_code:
        url = "https://map.yahooapis.jp/search/zip/V1/zipCodeSearch"
    else:
        url = "https://map.yahooapis.jp/geocode/V1/geoCoder"

    mocker.get(url + "?" + query, content=json.dumps(content).encode())


class TestGetYahooGeoData(unittest.TestCase):
    """
    get_yahoo_geo_dataのテスト
    """

    def test_valid_place(self):
        """正しい地名を指定した場合"""
        with requests_mock.Mocker() as mocker:
            place = "長野"
            result = {"place": "長野県長野市", "lat": "36.64858580", "lon": "138.19477310"}
            content = {
                "Feature": [
                    {
                        "Name": result["place"],
                        "Geometry": {
                            "Coordinates": ",".join([result["lon"], result["lat"]])
                        },
                    }
                ]
            }
            set_yahoo_mock(place, mocker, False, content)
            self.assertEqual(get_yahoo_geo_data(place), result)

    def test_valid_zip_code(self):
        """正しい郵便番号を指定した場合"""
        with requests_mock.Mocker() as mocker:
            place = "380-8512"
            result = {
                "place": "長野県長野市大字鶴賀緑町１６１３番地",
                "lat": "36.64858859",
                "lon": "138.19424819",
            }
            content = {
                "Feature": [
                    {
                        "Geometry": {
                            "Coordinates": ",".join([result["lon"], result["lat"]])
                        },
                        "Property": {"Address": result["place"]},
                    }
                ]
            }
            set_yahoo_mock(place, mocker, True, content)
            self.assertEqual(get_yahoo_geo_data(place), result)

    def test_invalid_place(self):
        """正しくない地名を指定した場合"""
        with requests_mock.Mocker() as mocker:
            place = "hoge"
            set_yahoo_mock(place, mocker, False)
            self.assertIsNone(get_yahoo_geo_data(place))


def set_gsi_mock(place: str, mocker: requests_mock.Mocker, content=None):
    """
    国土地理院用のMockを設定する
    :param place: 地名
    :param mocker: requestsのMocker
    :param content: req.contentの内容
    """
    if content is None:
        content = {}

    mocker.get(
        "https://msearch.gsi.go.jp/address-search/AddressSearch" + "?q=" + place,
        content=json.dumps(content).encode(),
    )


class TestGetGsiGeoData(unittest.TestCase):
    """
    get_gsi_geo_dataのテスト
    """

    def test_valid_place(self):
        """完全一致のある地名を指定した場合"""

        with requests_mock.Mocker() as mocker:
            place = "高ボッチ山"
            result = {
                "place": "高ボッチ山",
                "lat": "138.040319506908",
                "lon": "36.1321653109996",
            }
            content = [
                {
                    "geometry": {
                        "coordinates": [140.37767, 35.885433],
                        "type": "Point",
                    },
                    "type": "Feature",
                    "properties": {"addressCode": "", "title": "千葉県成田市高"},
                },
                {
                    "geometry": {
                        "coordinates": [140.560532, 35.681522],
                        "type": "Point",
                    },
                    "type": "Feature",
                    "properties": {"addressCode": "", "title": "千葉県匝瑳市高"},
                },
                {
                    "geometry": {
                        "coordinates": [135.702744, 34.553802],
                        "type": "Point",
                    },
                    "type": "Feature",
                    "properties": {"addressCode": "", "title": "奈良県香芝市高"},
                },
                {
                    "geometry": {
                        "coordinates": [result["lon"], result["lat"]],
                        "type": "Point",
                    },
                    "type": "Feature",
                    "properties": {
                        "addressCode": "20204",
                        "title": result["place"],
                        "dataSource": "4",
                    },
                },
                {
                    "geometry": {
                        "coordinates": [138.032837199722, 36.1328983561111],
                        "type": "Point",
                    },
                    "type": "Feature",
                    "properties": {
                        "addressCode": "20215",
                        "title": "高ボッチ牧場",
                        "dataSource": "1",
                    },
                },
            ]
            set_gsi_mock(place, mocker, content)
            self.assertEqual(get_gsi_geo_data(place), result)

    def test_invalid_place(self):
        """正しくない地名を指定した場合"""
        with requests_mock.Mocker() as mocker:
            place = "hoge"
            set_gsi_mock(place, mocker)
            self.assertIsNone(get_gsi_geo_data(place))


if __name__ == "__main__":
    unittest.main()
