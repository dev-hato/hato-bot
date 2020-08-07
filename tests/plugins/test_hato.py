"""
hato.pyのテスト
"""
import os
import unittest
from typing import List, Dict

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

    def amesh_test(self, place: str, coordinate: List[str], output: Dict[str, str], content=None):
        """
        ameshコマンドが実行できるかテスト
        :param place: コマンドの引数
        :param coordinate: [緯度, 経度]
        :param output: msg: Slackに投稿されて欲しいメッセージ, filename: Slackに投稿される画像のファイル名
        :param content: req.contentで返すデータ
        """
        with requests_mock.Mocker() as mocker:
            client1 = TestClient()
            mocker.get(weather_map_url(conf.YAHOO_API_TOKEN,
                                       *coordinate),
                       content=content)
            req = amesh(place)(client1)
            self.assertEqual(client1.get_post_message(), output['msg'])
            self.assertEqual(client1.get_filename(), output['filename'])
            self.assertEqual(req.status_code, 200)

    def amesh_upload_png_test(self, place: str, coordinate: List[str], msg: str):
        """
        ameshコマンドを実行し、png画像を「amesh.png」としてuploadできるかテスト
        :param place: コマンドの引数
        :param coordinate: [緯度, 経度]
        :param msg: Slackに投稿されて欲しいメッセージ
        """
        with open(os.path.join(os.path.dirname(__file__), 'test.png'), mode='rb') as picture_file:
            self.amesh_test(place,
                            coordinate,
                            {'msg': msg, 'filename': 'amesh.png'},
                            picture_file.read())

    def test_amesh_with_no_params(self):
        """
        引数なしでameshコマンドが実行できるかテスト
        """
        self.amesh_upload_png_test('',
                                   ['35.698856', '139.73091159273'],
                                   '東京の雨雲状況をお知らせするっぽ！')

    def test_amesh_with_params(self):
        """
        引数ありでameshコマンドが実行できるかテスト
        """
        coordinate = ['12.345', '123.456']
        self.amesh_upload_png_test(' '.join(coordinate),
                                   coordinate,
                                   '雨雲状況をお知らせするっぽ！')

    def test_amesh_upload_unknown_picture(self):
        """
        形式不明な画像データを取得した場合、「amesh」というファイル名でアップロードする
        """
        self.amesh_test('', ['35.698856', '139.73091159273'], {
                        'msg': '東京の雨雲状況をお知らせするっぽ！', 'filename': 'amesh'})

    def test_weather_map_url(self):
        """
        weather_map_urlを正しく作れるかテスト
        """
        appid = 'hoge'
        lat = '35.698856'
        lon = '139.73091159273'
        url = (
            'https://map.yahooapis.jp/map/V1/static?' +
            'appid={}&lat={}&lon={}&z=12&height=640&width=800&overlay=type:rainfall|datelabel:off'
        ).format(appid, lat, lon)
        self.assertEqual(weather_map_url(appid, lat, lon), url)


if __name__ == '__main__':
    unittest.main()
