# coding: utf-8
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
import unicodedata
import os
from logging import getLogger
from library.weather import get_city_id_from_city_name
from library.weather import get_weather
from library.amesh import get_map
from PIL import Image
from datetime import datetime

logger = getLogger(__name__)
VERSION = "0.2.0"

# 「hato help」を見つけたら、使い方を表示する
@respond_to('^help')
def help(message):
    user = message.user['name']
    logger.debug("%s called 'hato help'", user)
    message.send(
        '\n使い方\n'
        '```'
        'help       ... botの使い方を表示する。\n'
        '天気 [地名] ... 地名の天気予報を表示する。\n'
        '>< [文字列] ... 文字列を吹き出しで表示する。\n'
        'amesh      ... ameshを表示する。\n'
        'version    ... バージョン情報を表示する。\n'
        '```')

@respond_to('^天気 .+')
def weather(message):
    user = message.user['name']
    logger.debug("%s called 'hato 天気'", user)
    text = message.body['text']
    tmp, word = text.split(' ', 1)
    city_id = get_city_id_from_city_name(word)
    if city_id == None:
        message.send('該当する情報が見つからなかったっぽ！')
    else:
        weather_info = get_weather(city_id)
        message.send('```' + weather_info +'```')

# 「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する
@respond_to('^&gt;&lt; .+')
def totuzensi(message):
    user = message.user['name']
    text = message.body['text']
    tmp, word = text.split(' ', 1)
    logger.debug("%s called 'hato >< %s'", user, word)
    word = generator(word)
    msg = '\n```' + word + '```'
    message.send(msg)

@respond_to('^amesh$')
def amesh(message):
    user = message.user['name']
    channel = message.channel._body['name']
    logger.debug("%s called 'hato amesh'", user)
    message.send('東京の雨雲状況をお知らせするっぽ！(ちょっと時間かかるっぽ!)')
    # amesh画像を取得する
    file = get_map()

    message.channel.upload_file("amesh", file)

@respond_to('^version')
def version(message):
    user = message.user['name']
    logger.debug("%s called 'hato version'", user)
    message.send("Version " + VERSION)

# 突然の死で使う関数
# Todo: 別ファイルに移したい。
def text_length_list(text):
    count_list = list()

    for t in text:
        count = 0

        for c in t:
            count += 2 if unicodedata.east_asian_width(c) in 'FWA' else 1

        count_list.append(count)

    return count_list


def generator(msg):
    msg = msg.split('\n')
    msg_length_list = text_length_list(msg)
    max_length = max(msg_length_list)
    half_max_length = max_length // 2
    generating = '＿'

    for _ in range(half_max_length + 2):
        generating += '人'

    generating += '＿\n'

    for l, m in zip(msg_length_list, msg):
        half_length = (max_length - l) // 2
        generating += '＞'

        for _ in range(half_length + 2):
            generating += ' '

        generating += m

        for _ in range(max_length - half_length - l + 2):
            generating += ' '

        generating += '＜\n'

    generating += '￣'

    for _ in range(half_max_length + 2):
        generating += '^Y'

    generating += '￣'
    return generating
