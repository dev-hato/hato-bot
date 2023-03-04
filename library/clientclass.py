# coding: utf-8

"""
clientに使うclass
"""
import asyncio
import os
from abc import ABCMeta, abstractmethod

import discord
from slack import WebClient

import slackbot_settings as conf


class BaseClient(metaclass=ABCMeta):
    """
    client用の基底クラス
    """

    @abstractmethod
    def post(self, message: str):
        """投稿する"""
        raise NotImplementedError()

    @abstractmethod
    def get_send_user(self) -> str:
        """
        発火させたユーザーを返す
        """
        raise NotImplementedError()

    @abstractmethod
    def get_send_user_name(self) -> str:
        """
        発火させたユーザーの名前を返す
        """
        raise NotImplementedError()

    @abstractmethod
    def upload(self, file, filename):
        """ファイルを投稿する"""
        raise NotImplementedError()

    @staticmethod
    def get_type() -> str:
        """インスタンスの種類を返す"""
        return "test"


class SlackClient(BaseClient):
    """
    Slackを操作するClient
    """

    def __init__(self, channel, send_user):
        self.client = WebClient(token=conf.SLACK_API_TOKEN)
        self.slack_channel = channel
        self.send_user = send_user
        self.send_user_name = self.client.users_info(user=send_user)["user"]["name"]

    def post(self, message):
        """Slackにポストする"""
        self.client.chat_postMessage(channel=self.slack_channel, text=message)

    def upload(self, file, filename):
        """ファイルを投稿する"""
        self.client.files_upload(
            channels=self.slack_channel, file=file, filename=filename
        )

    def get_send_user(self):
        """botを呼び出したユーザーを返す"""
        return self.send_user

    def get_send_user_name(self):
        return self.send_user_name

    @staticmethod
    def get_type():
        """slack"""
        return "slack"


class ApiClient(BaseClient):
    """
    API形式のClient
    Slackに対する操作は行わない
    """

    def __init__(self):
        self.response = ""

    def post(self, message):
        """ポストする"""
        self.response = os.linesep.join([self.response, message])

    def upload(self, file, filename):
        """ファイルを投稿する"""
        self.response = os.linesep.join([self.response, f"upload: {filename}"])

    def get_send_user(self):
        """botを呼び出したユーザーを返す"""
        return "api_user_id"

    def get_send_user_name(self):
        return "api_user"

    @staticmethod
    def get_type():
        """api"""
        return "api"


class DiscordClient(BaseClient):
    """
    Discordを操作するClient
    """

    def __init__(self, discord_client, message: discord.Message):
        self.client = discord_client
        self.message = message

    def post(self, message):
        """Discordにポストする"""
        asyncio.create_task(self.message.channel.send(message))

    def upload(self, file, filename):
        """ファイルを投稿する"""
        asyncio.create_task(
            self.message.channel.send(file=discord.File(file, filename=filename))
        )

    def get_send_user(self):
        """botを呼び出したユーザーを返す"""
        return self.message.author.id

    def get_send_user_name(self):
        return self.message.author.name

    @staticmethod
    def get_type():
        """discord"""
        return "discord"
