"""
hato.pyのテスト
"""
import json
import os
import re
import unittest
from typing import List

import requests_mock

import slackbot_settings as conf
from plugins.hato import (
    altitude,
    amesh,
    omikuji,
    omikuji_results,
    split_command,
    yoshiyoshi,
)
from tests.library.test_geo import set_yahoo_mock
from tests.plugins import TestClient


class TestSplitCommand(unittest.TestCase):
    """
    split commandのテスト
    """

    def test_only_hankaku_space(self):
        """半角スペースのみのテストケース"""
        self.assertEqual(split_command(" 天気 東京"), ["天気", "東京"])

    def test_only_zenkaku_space(self):
        """全角スペースのみのテストケース"""
        self.assertEqual(split_command("　天気　東京"), ["天気", "東京"])

    def test_hankaku_and_zenkaku_space(self):
        """半角スペースと全角スペースが混ざったテストケース1"""
        self.assertEqual(split_command(" 天気　東京"), ["天気", "東京"])

    def test_zenkaku_and_hankaku_space(self):
        """半角スペースと全角スペースが混ざったテストケース2"""
        self.assertEqual(split_command("　天気 東京"), ["天気", "東京"])

    def test_last_hankaku_space(self):
        """行末に半角スペースが入ったテストケース"""
        self.assertEqual(split_command(" 天気 東京 "), ["天気", "東京"])

    def test_last_zenkaku_space(self):
        """行末に全角スペースが入ったテストケース"""
        self.assertEqual(split_command(" 天気 東京　"), ["天気", "東京"])

    def test_maxsplit(self):
        """空白が間に2つ以上ある場合"""
        self.assertEqual(split_command(" text add テスト", 1), ["text", "add テスト"])


class TestAmesh(unittest.TestCase):
    """
    ameshが正しく動作しているかテストする
    """

    def get_amesh_test(
        self,
        mocker: requests_mock.Mocker,
        place: str,
    ):
        """
        ameshを取得できるかテスト
        :param mocker requestsのMock
        :param place: コマンドの引数
        """
        client1 = TestClient()

        with open(os.path.join(os.path.dirname(__file__), "test.png"), mode="rb") as picture_file:
            image_content = picture_file.read()
            for image_url in [re.compile(r"www\.jma\.go\.jp/bosai/jmatile/data/nowc/.+\.png"),
                              re.compile(r"tile\.openstreetmap\.org/.+\.png")]:
                mocker.get(image_url, content=image_content)

        with open(os.path.join(os.path.dirname(__file__), "test_targetTimes_N1.json"), mode="rb") as json_file:
            jma_json_url = "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json"
            mocker.get(jma_json_url, content=json_file.read())

        actual = amesh(client1, place=place)
        self.assertEqual(None, actual)
        return client1

    def amesh_upload_png_test(self, mocker: requests_mock.Mocker, place: str, msg: str):
        """
        ameshコマンドを実行し、png画像を「amesh.png」としてuploadできるかテスト
        :param mocker requestsのMock
        :param place: コマンドの引数
        :param msg: Slackに投稿されて欲しいメッセージ
        """
        client1 = self.get_amesh_test(mocker, place)
        self.assertEqual(client1.get_post_message(), msg)
        self.assertEqual(client1.get_filename(), "amesh.png")

    def test_amesh_with_no_params(self):
        """
        引数なしでameshコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            content = {
                "Feature": [
                    {
                        "Name": "東京都世田谷区",
                        "Geometry": {"Coordinates": "139.65324950,35.64657460"},
                    }
                ]
            }
            set_yahoo_mock("東京", mocker, False, content)
            self.amesh_upload_png_test(mocker, "", "東京都世田谷区の雨雲状況をお知らせするっぽ！")

    def test_amesh_with_params(self):
        """
        引数ありでameshコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            coordinate = ["12.345", "123.456"]
            self.amesh_upload_png_test(mocker, " ".join(coordinate), "雨雲状況をお知らせするっぽ！")


class TestAltitude(unittest.TestCase):
    """
    標高が正しく動作しているかテストする
    """

    def altitude_test(
        self,
        mocker: requests_mock.Mocker,
        place: str,
        coordinates: List[str],
        content=None,
    ):
        """
        altitudeコマンドを実行し、正しくメッセージが投稿されるかテスト
        :param mocker requestsのMock
        :param place: コマンドの引数
        :param coordinates: [緯度, 経度]
        :param content: req.contentで返すデータ
        """
        client1 = TestClient()
        params = {
            "appid": conf.YAHOO_API_TOKEN,
            "coordinates": ",".join(reversed(coordinates)),
            "output": "json",
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        mocker.get(
            "https://map.yahooapis.jp/alt/V1/getAltitude?" + query,
            content=json.dumps(content).encode(),
        )
        # pylint: disable=E1121
        actual = altitude(client1, place)
        self.assertEqual(None, actual)
        return client1

    def test_altitude_with_no_params(self):
        """
        引数なしでaltitudeコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            coordinates = ["35.64657460", "139.65324950"]
            geo_content = {
                "Feature": [
                    {
                        "Name": "東京都世田谷区",
                        "Geometry": {"Coordinates": ",".join(reversed(coordinates))},
                    }
                ]
            }
            set_yahoo_mock("東京", mocker, False, geo_content)
            altitude_setagaya = 35.4
            altitude_content = {
                "Feature": [{"Property": {"Altitude": altitude_setagaya}}]
            }
            client1 = self.altitude_test(mocker, "", coordinates, altitude_content)
            self.assertEqual(
                client1.get_post_message(), f"東京都世田谷区の標高は{altitude_setagaya}mっぽ！"
            )

    def test_altitude_with_params(self):
        """
        引数ありでaltitudeコマンドが実行できるかテスト
        """
        with requests_mock.Mocker() as mocker:
            coordinates = ["12.345", "123.456"]
            altitude_ = 122
            altitude_content = {"Feature": [{"Property": {"Altitude": altitude_}}]}
            client1 = self.altitude_test(
                mocker, " ".join(coordinates), coordinates, altitude_content
            )
            self.assertEqual(
                client1.get_post_message(),
                f'{", ".join(coordinates)}の標高は{altitude_}mっぽ！',
            )


class TestYoshiyoshi(unittest.TestCase):
    """
    yoshiyoshiのテスト
    """

    def test_yoshiyoshi(self):
        """正常系のテストケース"""
        client1 = TestClient()
        # pylint: disable=E1121
        yoshiyoshi(client1)
        self.assertEqual(client1.get_post_message(), "よしよし")


class TestOmikuji(unittest.TestCase):
    """
    omikujiのテスト
    """

    def test_omikuji(self):
        """
        設定したおみくじ結果のうち1つが返ってくる
        """

        client1 = TestClient()
        # pylint: disable=E1121
        omikuji(client1)
        self.assertIn(
            client1.get_post_message(),
            map(lambda e: e.message, omikuji_results.values()),
        )


if __name__ == "__main__":
    unittest.main()
