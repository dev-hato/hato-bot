"""
hato.pyのテスト
"""

import unittest

import requests_mock

import slackbot_settings as conf
from plugins.hato import split_command, amesh, weather_map_url
from tests.plugins import TestClient


class TestSplitCommand(unittest.TestCase):
    """
    split commandのテスト
    """

    def test_only_hankaku_space(self):
        """ 半角スペースのみのテストケース """
        self.assertEqual(split_command(' 天気 東京'), ['天気', '東京'])

    def test_only_zenkaku_space(self):
        """ 全角スペースのみのテストケース """
        self.assertEqual(split_command('　天気　東京'), ['天気', '東京'])

    def test_hankaku_and_zenkaku_space(self):
        """ 半角スペースと全角スペースが混ざったテストケース1 """
        self.assertEqual(split_command(' 天気　東京'), ['天気', '東京'])

    def test_zenkaku_and_hankaku_space(self):
        """ 半角スペースと全角スペースが混ざったテストケース2 """
        self.assertEqual(split_command('　天気 東京'), ['天気', '東京'])

    def test_last_hankaku_space(self):
        """ 行末に半角スペースが入ったテストケース """
        self.assertEqual(split_command(' 天気 東京 '), ['天気', '東京'])

    def test_last_zenkaku_space(self):
        """ 行末に全角スペースが入ったテストケース """
        self.assertEqual(split_command(' 天気 東京　'), ['天気', '東京'])

    def test_maxsplit(self):
        """ 空白が間に2つ以上ある場合 """
        self.assertEqual(split_command(' text add テスト', 1),
                         ['text', 'add テスト'])


class TestAmesh(unittest.TestCase):
    """
    ameshが正しく動作しているかテストする
    """

    def amesh_test(self, place, lat, lon, msg):
        """
        ameshコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            client1 = TestClient()
            mocker.get(weather_map_url(conf.YAHOO_API_TOKEN, lat, lon))
            req = amesh(place)(client1)
            self.assertEqual(client1.get_post_message(), msg)
            self.assertEqual(req.status_code, 200)

    def test_amesh_with_no_params(self):
        """
        引数なしでameshコマンドが実行できるかテスト
        """
        self.amesh_test('',
                        '35.698856',
                        '139.73091159273',
                        '東京の雨雲状況をお知らせするっぽ！')

    def test_amesh_with_params(self):
        """
        引数ありでameshコマンドが実行できるかテスト
        """
        self.amesh_test('12.345 123.456',
                        '12.345',
                        '123.456',
                        '雨雲状況をお知らせするっぽ！')

    def test_weather_map_url(self):
        """
        weather_map_urlを正しく作れるかテスト
        """
        appid = 'hoge'
        lat = '35.698856'
        lon = '139.73091159273'
        self.assertEqual(weather_map_url(appid, lat, lon),
                         (
            'https://map.yahooapis.jp/map/V1/static?' +
            'appid={}&lat={}&lon={}&z=12&height=640&width=800&overlay=type:rainfall|datelabel:off'
        ).format(appid, lat, lon))


if __name__ == '__main__':
    unittest.main()
