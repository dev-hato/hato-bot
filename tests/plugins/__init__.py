"""
plugin関連のテスト
"""

from library.clientclass import BaseClient


class TestClient(BaseClient):
    """
    モッククライアント
    """

    def __init__(self):
        self.post_message = ""
        self.filename = ""

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
        self.filename = filename

    def get_filename(self):
        """アップロードする画像のファイル名を返す"""
        return self.filename
