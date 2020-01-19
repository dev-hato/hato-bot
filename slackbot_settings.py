# coding: utf-8
import os
import urllib.parse
from dotenv import load_dotenv, find_dotenv

# .envファイルがあれば読み込む。存在しなければ環境変数から読み込む。
load_dotenv(find_dotenv())
# SlackのAPI Tokenを指定する。
API_TOKEN = str(os.environ['SLACKBOT_API_TOKEN'])
# データベースの接続情報
# postgres://user:pwd@host:port/db
db_auth = urllib.parse.urlparse(str(os.environ['DATABASE_URL']))
DB_HOST = db_auth.hostname or 'localhost'
DB_USER = db_auth.username or 'root'
DB_PASSWORD = db_auth.password or ''
DB_PORT = db_auth.port or 5432
DB_NAME = db_auth.path[1:]
DB_SSL = bool(db_auth.path[1:]) #DB_NAMEが空の場合はSSLを無効にする(for Develop)

# Slack bot用の設定
DEFAULT_REPLY = "使い方がわからない時は `help` とメンションするっぽ!"
PLUGINS = ['plugins']
