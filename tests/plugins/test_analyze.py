"""
analyze.pyのテスト
"""

import unittest

from plugins import hato
from plugins.analyze import analyze_message, analyze_slack_message
from tests.plugins import TestClient


class TestAnalyzeSlackMessage(unittest.TestCase):
    """
    Slackコマンドを正しく解析できるかテストする
    """

    def test_telephone_link(self):
        """電話番号のリンクを含むコマンドを正しく解析できる"""
        client1 = TestClient()
        messages = [
            {"type": "text", "text": ">< "},
            {"type": "link", "url": "tel:09012345678", "text": "09012345678"},
        ]
        analyze_slack_message(messages)(client1)
        client2 = TestClient()
        # pylint: disable=E1121
        hato.totuzensi(client2, "09012345678")
        self.assertEqual(client1.get_post_message(), client2.get_post_message())

    def test_code(self):
        """コードを含むコマンドを正しく解析できる"""
        client1 = TestClient()
        messages = [
            {"type": "text", "text": ">< "},
            {"type": "text", "text": "09012345678", "style": {"code": True}},
        ]
        analyze_slack_message(messages)(client1)
        client2 = TestClient()
        # pylint: disable=E1121
        hato.totuzensi(client2, "09012345678")
        self.assertEqual(client1.get_post_message(), client2.get_post_message())


class TestAnaryzeMessage(unittest.TestCase):
    """
    コマンドを正しく解析できるかテストする
    """

    def test_version(self):
        """versionが正しく返せるかテスト"""
        self.assertEqual(analyze_message("version"), hato.version)

    def test_totuzensi(self):
        """>< コマンドが実行できるかテスト"""

        client1 = TestClient()
        analyze_message(">< aaa")(client1)
        client2 = TestClient()
        # pylint: disable=E1121
        hato.totuzensi(client2, "aaa")
        self.assertEqual(client1.get_post_message(), client2.get_post_message())
        # self.assertEqual(analyze_message('>< aaa'), hato.totuzensi('aaa'))
        # 本当はこうしたいが、関数オブジェクトが違っているので落ちてしまう。
        # なので実行結果で見るしかない


if __name__ == "__main__":
    unittest.main()
