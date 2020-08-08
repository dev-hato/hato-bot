"""
amesh.pyのテスト
"""
import json
import unittest

import requests_mock

import slackbot_settings as conf
from library.amesh import get_geo_data


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
                        'Id': '20201',
                        'Gid': '',
                        'Name': result['place'],
                        'Geometry': {
                            'Type': 'point',
                            'Coordinates': ','.join([result['lon'], result['lat']]),
                            'BoundingBox': '137.91001700,36.46045600 138.31907300,36.83584800'
                        },
                        'Category': [],
                        'Description': '',
                        'Style': [],
                        'Property': {
                            'Uid': 'b6fda7805e602cfa221a1cf027772fdc928b0870',
                            'CassetteId': 'b22fee69b0dcaf2c2fe2d6a27906dafc',
                            'Yomi': 'ナガノケンナガノシ',
                            'Country': {'Code': 'JP', 'Name': '日本'},
                            'Address': '長野県長野市',
                            'GovernmentCode': '20201',
                            'AddressMatchingLevel': '2',
                            'AddressType': '市'
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
