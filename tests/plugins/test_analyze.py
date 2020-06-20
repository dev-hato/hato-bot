"""
analyze.pyのテスト
"""

import unittest

from plugins.analyze import analyze_message
import plugins.hato as hato
from library.clientclass import BaseClient


class TestClient(BaseClient):
    """
    モッククライアント
    """

    def __init__(self):
        self.post_message = ""

    def post(self, message: str):
        self.post_message = message

    def get_post_message(self):
        """投稿される文章を返す"""

        return self.post_message

    @staticmethod
    def get_send_user_name():
        return "test user"

    @staticmethod
    def get_send_user():
        return "abc123"

    def upload(self, file, filename):
        return


class TestAnaryzeMessage(unittest.TestCase):
    """
    コマンドを正しく解析できるかテストする
    """

    def test_version(self):
        """versionが正しく返せるかテスト"""
        self.assertEqual(analyze_message('version'), hato.version)

    def test_totuzensi(self):
        """>< コマンドが実行できるかテスト"""

        client1 = TestClient()
        analyze_message('>< aaa')(client1)
        client2 = TestClient()
        hato.totuzensi('aaa')(client2)
        self.assertEqual(client1.get_post_message(),
                         client2.get_post_message())
        # self.assertEqual(analyze_message('>< aaa'), hato.totuzensi('aaa'))
        # 本当はこうしたいが、関数オブジェクトが違っているので落ちてしまう。
        # なので実行結果で見るしかない


if __name__ == '__main__':
    unittest.main()
