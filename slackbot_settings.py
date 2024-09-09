# coding: utf-8

"""
env情報ファイル
"""

import os
import ssl
import urllib.parse

from dotenv import find_dotenv, load_dotenv

# .envファイルがあれば読み込む。存在しなければ環境変数から読み込む。
load_dotenv(find_dotenv())
# SlackのAPI Tokenを指定する。
SLACK_API_TOKEN = str(os.environ["SLACK_API_TOKEN"])
SLACK_SIGNING_SECRET = str(os.environ["SLACK_SIGNING_SECRET"])
# データベースの接続情報(URL形式)
# postgres://user:password@host:port/dbname
DB_URL = str(os.environ["DATABASE_URL"])
db_auth = urllib.parse.urlparse(DB_URL)
DB_HOST = db_auth.hostname
DB_USER = db_auth.username
DB_PASSWORD = db_auth.password
DB_PORT = db_auth.port
DB_NAME = db_auth.path[1:]
DB_SSL = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
PORT = int(os.environ.get("PORT", "3000"))

# Yahoo APIを用いるためのTokenを指定する。
YAHOO_API_TOKEN = str(os.environ["YAHOO_API_TOKEN"])

# Slack bot用の設定
DEFAULT_REPLY = "使い方がわからない時は `help` とメンションするっぽ!"
PLUGINS = ["plugins"]

# ChatGPT用の設定
OPENAI_API_KEY = str(os.environ["OPENAI_API_KEY"])

# Discord用の設定
DISCORD_API_TOKEN = str(os.environ["DISCORD_API_TOKEN"])

# Misskey用の設定
MISSKEY_DOMAIN = str(os.environ["MISSKEY_DOMAIN"])
MISSKEY_API_TOKEN = str(os.environ["MISSKEY_API_TOKEN"])
MISSKEY_FEDERATION = str(os.environ.get("MISSKEY_FEDERATION","false"))

MODE = str(os.environ["MODE"])

GIT_COMMIT_HASH = os.environ.get("GIT_COMMIT_HASH")

VERSION = "3.0.4"
