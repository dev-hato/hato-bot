# coding: utf-8

"""hatobotのチャット部分"""

import os
import re
from logging import getLogger
import datetime
import requests
from slackbot.bot import respond_to
import slackbot_settings as conf
from library.weather import get_city_id_from_city_name, get_weather
from library.labotter import labo_in, labo_rida
from library.vocabularydb import get_vocabularys, add_vocabulary, show_vocabulary, delete_vocabulary, show_random_vocabulary
from library.earthquake import generate_quake_info_for_slack, get_quake_list
from library.hukidasi import generator
from library.hatokaraage import hato_ha_karaage

logger = getLogger(__name__)
VERSION = "1.0.3"

space_pattern = re.compile(r'[ 　]')


def respond_to_with_space(matchstr, flags=0):
    """スペースを削除する"""

    return respond_to(matchstr.replace(' ', '[ 　]').replace('^', r'^\s*'), flags)


@respond_to_with_space('^help')
def help_message(message):
    """「hato help」を見つけたら、使い方を表示する"""

    user = message.user['name']
    logger.debug("%s called 'hato help'", user)
    str_help = '\n使い方\n'\
        '```'\
        '天気 [text] ... 地名の天気予報を表示する。\n'\
        'amesh ... ameshを表示する。\n'\
        'eq ... 最新の地震情報を3件表示する。\n'\
        'text list ... パワーワード一覧を表示する。 \n'\
        'text random ... パワーワードをひとつ、ランダムで表示する。 \n'\
        'text show [int] ... 指定した番号[int]のパワーワードを表示する。 \n'\
        'text add [text] ... パワーワードに[text]を登録する。 \n'\
        'text delete [int] ... 指定した番号[int]のパワーワードを削除する。 \n'\
        'in ... らぼいんする\n'\
        'rida ... らぼいんからの経過時間を表示する\n'\
        '>< [text] ... 文字列[text]を吹き出しで表示する。\n'\
        'version ... バージョン情報を表示する。\n'\
        '\n詳細はドキュメント(https://github.com/nakkaa/hato-bot/wiki)も見てくれっぽ!```\n'
    message.send(str_help)


@respond_to_with_space('^eq$|^地震$')
def earth_quake(message):
    """地震 地震情報を取得する"""

    msg = "地震情報を取得できなかったっぽ!"
    result, data = get_quake_list()
    if result:
        msg = "地震情報を取得したっぽ!\n"
        msg = msg + generate_quake_info_for_slack(data, 3)
    message.send(msg)


@respond_to_with_space('^in$')
def labotter_in(message):
    """らぼいん！"""

    msg = "らぼいんに失敗したっぽ!(既に入っているかもしれないっぽ)"
    user_id = message.user['id']
    flag, start_time = labo_in(user_id)
    if flag:
        msg = "らぼいんしたっぽ! \nいん時刻: {}".format(start_time)
    message.send(msg)


@respond_to_with_space('^rida$')
def labotter_rida(message):
    """らぼりだ！"""

    msg = "らぼりだに失敗したっぽ!"
    user_id = message.user['id']
    flag, end_time, datetime_second, sum_second = labo_rida(user_id)
    diff_time = datetime.timedelta(seconds=datetime_second)
    sum_time = datetime.timedelta(seconds=sum_second)
    if flag:
        msg = "らぼりだしたっぽ! お疲れ様っぽ!\nりだ時刻: {} \n拘束時間: {}\n累計時間: {}".format(
            end_time, diff_time, sum_time)
    message.send(msg)


@respond_to_with_space('^text list$')
def get_text_list(message):
    """パワーワードのリストを表示"""

    user = message.user['name']
    logger.debug("%s called 'text list'", user)
    msg = get_vocabularys()
    message.send(msg)


@respond_to_with_space('^text add .+')
def add_text(message):
    """パワーワードの追加"""

    user = message.user['name']
    logger.debug("%s called 'text add'", user)
    text = message.body['text']
    _, _, word = space_pattern.split(text, 2)
    add_vocabulary(word)
    message.send("覚えたっぽ!")


@respond_to_with_space('^text show .+')
def show_text(message):
    """指定した番号のパワーワードを表示する"""

    user = message.user['name']
    logger.debug("%s called 'text show'", user)
    text = message.body['text']
    _, _, power_word_id = space_pattern.split(text, 2)
    msg = show_vocabulary(int(power_word_id))
    message.send(msg)


@respond_to_with_space('^text$|^text random$')
def show_random_text(message):
    """パワーワードの一覧からランダムで1つを表示する"""
    user = message.user['name']
    logger.debug("%s called 'text random'", user)
    msg = show_random_vocabulary()
    message.send(msg)


@respond_to_with_space('^text delete .+')
def delete_text(message):
    """指定した番号のパワーワードを削除する"""

    user = message.user['name']
    logger.debug("%s called 'text delete'", user)
    text = message.body['text']
    _, _, power_word_id = space_pattern.split(text, 2)
    msg = delete_vocabulary(int(power_word_id))
    message.send(msg)


@respond_to_with_space('^天気 .+')
def weather(message):
    """指定した都市の天気を表示する"""

    user = message.user['name']
    logger.debug("%s called 'hato 天気'", user)
    text = message.body['text']
    _, word = space_pattern.split(text, 1)
    city_id = get_city_id_from_city_name(word)
    if city_id is None:
        message.send('該当する情報が見つからなかったっぽ！')
    else:
        weather_info = get_weather(city_id)
        message.send('```' + weather_info + '```')


@respond_to_with_space('^&gt;&lt; .+')
def totuzensi(message):
    """「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する"""

    user = message.user['name']
    text = message.body['text']
    _, word = space_pattern.split(text, 1)
    word = hato_ha_karaage(word)
    logger.debug("%s called 'hato >< %s'", user, word)
    word = generator(word)
    msg = '\n```' + word + '```'
    message.send(msg)


def weather_map_url(appid: str, lat: str, lon: str) -> str:
    """weather_map_urlを作る"""
    return (
        'https://map.yahooapis.jp/map/V1/static?' +
        'appid={}&lat={}&lon={}&z=12&height=640&width=800&overlay=type:rainfall|datelabel:off'
    ).format(appid, lat, lon)


@respond_to_with_space('^amesh$')
def amesh(message):
    """東京の天気を表示する"""

    user = message.user['name']
    logger.debug("%s called 'hato amesh'", user)
    message.send('東京の雨雲状況をお知らせするっぽ！')

    url = weather_map_url(conf.YAHOO_API_TOKEN, '35.698856', '139.73091159273')
    req = requests.get(url, stream=True)
    f_name = "amesh.jpg"
    if req.status_code == 200:
        with open(f_name, 'wb') as weather_map_file:
            weather_map_file.write(req.content)

    message.channel.upload_file("amesh", f_name)

    if os.path.exists(f_name):
        os.remove(f_name)


@respond_to('^amesh kyoto$')
def amesh_kyoto(message):
    """京都の天気を表示する"""

    user = message.user['name']
    logger.debug("%s called 'hato amesh kyoto'", user)
    message.send('京都の雨雲状況をお知らせするっぽ！')

    url = weather_map_url(conf.YAHOO_API_TOKEN, '34.966944', '135.773056')
    req = requests.get(url, stream=True)
    f_name = "amesh.jpg"
    if req.status_code == 200:
        with open(f_name, 'wb') as weather_map_file:
            weather_map_file.write(req.content)

    message.channel.upload_file("amesh", f_name)
    os.remove(f_name)


@respond_to('^amesh .+ .+')
def amesh_with_gis(message):
    """位置を指定したameshを表示する"""

    user = message.user['name']
    text = message.body['text']
    logger.debug("%s called 'hato amesh '", user)
    message.send('雨雲状況をお知らせするっぽ！')
    _, lat, lon = space_pattern.split(text, 2)

    url = weather_map_url(conf.YAHOO_API_TOKEN, lat, lon)
    req = requests.get(url, stream=True)
    f_name = "amesh.jpg"
    if req.status_code == 200:
        with open(f_name, 'wb') as weather_map_file:
            weather_map_file.write(req.content)

    message.channel.upload_file("amesh", f_name)
    os.remove(f_name)


@respond_to_with_space('^version')
def version(message):
    """versionを表示する"""

    user = message.user['name']
    logger.debug("%s called 'hato version'", user)
    str_ver = "バージョン情報\n```"\
        "Version {}\n"\
        "Copyright (C) 2020 hato-bot Development team\n"\
        "https://github.com/nakkaa/hato-bot ```".format(VERSION)
    message.send(str_ver)
