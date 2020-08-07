"""
plugin関連のテスト
"""

from library.clientclass import BaseClient


class TestClient(BaseClient):
    """
    モッククライアント
    """

    def __init__(self):
        self.post_message: str = ""
        self.filename: str = ""

    def post(self, message: str):
        self.post_message = message

    def get_post_message(self) -> str:
        """投稿される文章を返す"""

        return self.post_message

    @staticmethod
    def get_send_user_name() -> str:
        return "test user"

    @staticmethod
    def get_send_user() -> str:
        return "abc123"

    def upload(self, file, filename):
        self.filename = filename

    def get_filename(self) -> str:
        """アップロードする画像のファイル名を返す"""
        return self.filename
