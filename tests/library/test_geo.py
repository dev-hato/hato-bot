"""
amesh.pyのテスト
"""
import json
import unittest

import requests_mock

import slackbot_settings as conf
from library.geo import get_geo_data


def set_mock(place: str, mocker: requests_mock.Mocker, content=None):
    """
    Mockを設定する
    :param place: 地名・住所
    :param mocker: requestsのMocker
    :param content: req.contentの内容
    """
    if content is None:
        content = {}

    params = {
        'appid': conf.YAHOO_API_TOKEN,
        'query': place,
        'output': 'json'
    }
    query = '&'.join([f'{k}={v}' for k, v in params.items()])
    mocker.get(
        'https://map.yahooapis.jp/geocode/V1/geoCoder?' + query,
        content=json.dumps(content).encode()
    )


class TestGetGeoData(unittest.TestCase):
    """
    get_geo_dataのテスト
    """

    def test_valid_place(self):
        """ 正しい地名を指定した場合 """
        with requests_mock.Mocker() as mocker:
            place = '長野'
            result = {'place': '長野県長野市',
                      'lat': '36.64858580', 'lon': '138.19477310'}
            content = {
                'Feature': [
                    {
                        'Name': result['place'],
                        'Geometry': {
                            'Coordinates': ','.join([result['lon'], result['lat']])
                        }
                    }
                ]
            }
            set_mock(place, mocker, content)
            self.assertEqual(get_geo_data(place), result)

    def test_valid_zip_code(self):
        """ 正しい郵便番号を指定した場合 """
        with requests_mock.Mocker() as mocker:
            place = '380-8512'
            result = {'place': '長野県長野市大字鶴賀緑町１６１３番地',
                      'lat': '36.64858859', 'lon': '138.19424819'}
            content = {
                'Feature': [
                    {
                        'Geometry': {
                            'Coordinates': ','.join([result['lon'], result['lat']])
                        },
                        'Property': {
                            'Address': result['place']
                        }
                    }
                ]
            }
            set_mock(place, mocker, content)
            self.assertEqual(get_geo_data(place), result)

    def test_invalid_place(self):
        """ 正しくない地名を指定した場合 """
        with requests_mock.Mocker() as mocker:
            place = 'hoge'
            set_mock(place, mocker)
            self.assertIsNone(get_geo_data(place))


if __name__ == '__main__':
    unittest.main()
