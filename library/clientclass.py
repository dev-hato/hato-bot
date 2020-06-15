# coding: utf-8

"""
clientに使うclass
"""
from abc import ABCMeta, abstractmethod
from slack import WebClient
import slackbot_settings as conf


class BaseClient(metaclass=ABCMeta):
    """
    client用の基底クラス
    """

    @abstractmethod
    def post(self, message: str):
        """投稿する"""
        pass

    @abstractmethod
    def get_send_user(self) -> str:
        """
        発火させたユーザーを返す
        """
        pass

    def get_type(self) -> str:
        """インスタンスの種類を返す"""
        return 'test'


class SlackClient(BaseClient):
    """
    Slackを操作するClient
    """

    def __init__(self, channel, send_user):
        self.client = WebClient(token=conf.SLACK_API_TOKEN)
        self.slack_channel = channel
        self.send_user = send_user

    def post(self, message):
        """Slackにポストする"""
        self.client.chat_postMessage(
            channel=self.slack_channel,
            text=message
        )

    def get_send_user(self):
        """botを呼び出したユーザーを返す"""
        return self.send_user

    def get_type(self):
        """slack"""
        return 'slack'
