"""
run.pyのテスト
"""

import unittest

from plugins import hato
from run import analyze_slack_message
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
