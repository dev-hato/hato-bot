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

    def get_send_user_name(self) -> str:
        return "test user"

    def get_send_user(self) -> str:
        return "abc123"

    def upload(self, file: str, filename: str):
        self.filename = filename

    def get_filename(self) -> str:
        """アップロードする画像のファイル名を返す"""
        return self.filename
