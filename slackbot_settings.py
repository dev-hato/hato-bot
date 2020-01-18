# coding: utf-8
import os
from dotenv import load_dotenv, find_dotenv

# SlackのAPI Tokenを指定する。
# API Tokenが記載された .envファイルがあれば読み込む。存在しなければ環境変数から読み込む。
load_dotenv(find_dotenv())
API_TOKEN = str(os.environ['SLACKBOT_API_TOKEN'])

DEFAULT_REPLY = "鳩は唐揚げ"
PLUGINS = ['plugins']
