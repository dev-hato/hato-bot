# coding: utf-8
import os
import urllib.parse
from dotenv import load_dotenv, find_dotenv

# .envファイルがあれば読み込む。存在しなければ環境変数から読み込む。
load_dotenv(find_dotenv())
# SlackのAPI Tokenを指定する。
API_TOKEN = str(os.environ['SLACKBOT_API_TOKEN'])
# データベースの接続情報(URL形式)
# postgres://user:password@host:port/dbname
db_auth = urllib.parse.urlparse(str(os.environ['DATABASE_URL']))
DB_HOST = db_auth.hostname
DB_USER = db_auth.username
DB_PASSWORD = db_auth.password
DB_PORT = db_auth.port
DB_NAME = db_auth.path[1:]

# DB_NAMEが空の場合はSSLを無効にする(for Develop)。Herokuの場合はTrue。
DB_SSL = bool(db_auth.path[1:])

# Yahoo APIを用いるためのTokenを指定する。
YAHOO_API_TOKEN = str(os.environ['YAHOO_API_TOKEN'])

# Slack bot用の設定
DEFAULT_REPLY = "使い方がわからない時は `help` とメンションするっぽ!"
PLUGINS = ['plugins']
