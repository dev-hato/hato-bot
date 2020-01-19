# coding: utf-8
import os
from dotenv import load_dotenv, find_dotenv

# .envファイルがあれば読み込む。存在しなければ環境変数から読み込む。
load_dotenv(find_dotenv())
# SlackのAPI Tokenを指定する。
API_TOKEN = str(os.environ['SLACKBOT_API_TOKEN'])
# データベースの接続情報
DB_HOST = str(os.environ['DB_HOST'])
DB_USER = str(os.environ['DB_USER'])
DB_PASSWORD = str(os.environ['DB_PASSWORD'])

# Slack bot用の設定
DEFAULT_REPLY = "使い方がわからない時は `help` とメンションするっぽ!"
PLUGINS = ['plugins']
