"""
hato.pyのテスト
"""
import os
import unittest
from typing import List

import requests_mock

import slackbot_settings as conf
from plugins.hato import split_command, amesh
from tests.library.test_amesh import set_mock
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

    def get_amesh_test(self,
                       mocker: requests_mock.Mocker,
                       place: str,
                       coordinate: List[str],
                       content=None):
        """
        ameshを取得できるかテスト
        :param mocker requestsのMock
        :param place: コマンドの引数
        :param coordinate: [緯度, 経度]
        :param content: req.contentで返すデータ
        """
        client1 = TestClient()
        params = {
            'appid': conf.YAHOO_API_TOKEN,
            'lat': coordinate[0],
            'lon': coordinate[1],
            'z': 12,
            'height': 640,
            'width': 800,
            'overlay': 'type:rainfall|datelabel:off'
        }
        query = '&'.join([f'{k}={v}' for k, v in params.items()])
        mocker.get(
            'https://map.yahooapis.jp/map/V1/static?' + query,
            content=content
        )
        req = amesh(place)(client1)
        self.assertEqual(req.status_code, 200)
        return client1

    def amesh_upload_png_test(self,
                              mocker: requests_mock.Mocker,
                              place: str,
                              coordinate: List[str],
                              msg: str):
        """
        ameshコマンドを実行し、png画像を「amesh.png」としてuploadできるかテスト
        :param mocker requestsのMock
        :param place: コマンドの引数
        :param coordinate: [緯度, 経度]
        :param msg: Slackに投稿されて欲しいメッセージ
        """
        with open(os.path.join(os.path.dirname(__file__), 'test.png'), mode='rb') as picture_file:
            client1 = self.get_amesh_test(mocker,
                                          place,
                                          coordinate,
                                          picture_file.read())
            self.assertEqual(client1.get_post_message(), msg)
            self.assertEqual(client1.get_filename(), 'amesh.png')

    def test_amesh_with_no_params(self):
        """
        引数なしでameshコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            content = {
                'Feature': [
                    {
                        'Name': '東京都世田谷区',
                        'Geometry': {
                            'Coordinates': '139.65324950,35.64657460'
                        }
                    }
                ]
            }
            set_mock('東京', mocker, content)
            self.amesh_upload_png_test(mocker,
                                       '',
                                       ['35.64657460', '139.65324950'],
                                       '東京都世田谷区の雨雲状況をお知らせするっぽ！')

    def test_amesh_with_params(self):
        """
        引数ありでameshコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            coordinate = ['12.345', '123.456']
            self.amesh_upload_png_test(mocker,
                                       ' '.join(coordinate),
                                       coordinate,
                                       '雨雲状況をお知らせするっぽ！')

    def test_amesh_upload_unknown_picture(self):
        """
        形式不明な画像データを取得した場合、「amesh」というファイル名でアップロードする
        """
        with requests_mock.Mocker() as mocker:
            coordinate = ['12.345', '123.456']
            client1 = self.get_amesh_test(mocker,
                                          ' '.join(coordinate),
                                          coordinate)
            self.assertEqual(client1.get_post_message(), '雨雲状況をお知らせするっぽ！')
            self.assertEqual(client1.get_filename(), 'amesh')


if __name__ == '__main__':
    unittest.main()
