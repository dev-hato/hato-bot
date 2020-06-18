# coding: utf-8

"""hatobotのチャット部分"""

import os
import re
from logging import getLogger
import datetime
from typing import List
import requests
import slackbot_settings as conf
from library.weather import get_city_id_from_city_name, get_weather
from library.labotter import labo_in, labo_rida
from library.vocabularydb import get_vocabularys, add_vocabulary, show_vocabulary, delete_vocabulary, show_random_vocabulary
from library.earthquake import generate_quake_info_for_slack, get_quake_list
from library.hukidasi import generator
from library.hatokaraage import hato_ha_karaage
from library.clientclass import BaseClient

logger = getLogger(__name__)
VERSION = "1.0.4"


def respond_to_with_space(matchstr: str) -> str:
    """スペースを削除する"""

    space = ' '
    return matchstr.replace('^', f'^{space}').replace(space, r'\s*')


def split_command(command: str, maxsplit: int = 0) -> List[str]:
    """コマンドを分離する"""

    return re.split(r'\s+', command.strip().strip('　'), maxsplit)


def help_message(client: BaseClient):
    """「hato help」を見つけたら、使い方を表示する"""

    logger.debug("%s called 'hato help'", client.get_send_user())
    logger.debug("%s app called 'hato help'", client.get_type())
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
    client.post(str_help)


def default_action(client: BaseClient):
    """どのコマンドにもマッチしなかった"""
    client.post(conf.DEFAULT_REPLY)


def earth_quake(client: BaseClient):
    """地震 地震情報を取得する"""

    msg = "地震情報を取得できなかったっぽ!"
    data = get_quake_list()
    if data is not None:
        msg = "地震情報を取得したっぽ!\n"
        msg = msg + generate_quake_info_for_slack(data, 3)

    client.post(msg)


def labotter_in(client: BaseClient):
    """らぼいん！"""

    msg = "らぼいんに失敗したっぽ!(既に入っているかもしれないっぽ)"
    user_id = client.get_send_user()
    flag, start_time = labo_in(user_id)
    if flag:
        msg = "らぼいんしたっぽ! \nいん時刻: {}".format(start_time)

    client.post(msg)


def labotter_rida(client: BaseClient):
    """らぼりだ！"""

    msg = "らぼりだに失敗したっぽ!"
    user_id = client.get_send_user()
    flag, end_time, datetime_second, sum_second = labo_rida(user_id)
    diff_time = datetime.timedelta(seconds=datetime_second)
    sum_time = datetime.timedelta(seconds=sum_second)
    if flag:
        msg = "らぼりだしたっぽ! お疲れ様っぽ!\nりだ時刻: {} \n拘束時間: {}\n累計時間: {}".format(
            end_time, diff_time, sum_time)

    client.post(msg)


def get_text_list(client: BaseClient):
    """パワーワードのリストを表示"""

    user = client.get_send_user_name()
    logger.debug("%s called 'text list'", user)
    msg = get_vocabularys()

    client.post(msg)


def add_text(word: str):
    """パワーワードの追加"""

    def ret(client: BaseClient):
        add_vocabulary(word)
        user = client.get_send_user_name()
        logger.debug("%s called 'text add'", user)
        client.post('覚えたっぽ!')

    return ret


def show_text(power_word_id: str):
    """指定した番号のパワーワードを表示する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'text show'", user)
        msg = show_vocabulary(int(power_word_id))
        client.post(msg)
    return ret


def show_random_text(client: BaseClient):
    """パワーワードの一覧からランダムで1つを表示する"""
    user = client.get_send_user_name()
    logger.debug("%s called 'text random'", user)
    msg = show_random_vocabulary()
    client.post(msg)


def delete_text(power_word_id: str):
    """指定した番号のパワーワードを削除する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'text delete'", user)
        msg = delete_vocabulary(int(power_word_id))
        client.post(msg)
    return ret


def weather(place: str):
    """指定した都市の天気を表示する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'hato 天気'", user)
        city_id = get_city_id_from_city_name(place)
        if city_id is None:
            client.post('該当する情報が見つからなかったっぽ！')
        else:
            weather_info = get_weather(city_id)
            client.post('```' + weather_info + '```')
    return ret


def totuzensi(message: str):
    """「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        word = hato_ha_karaage(message)
        logger.debug("%s called 'hato >< %s'", user, word)
        print(word)
        msg = generator(word)
        print(msg)
        client.post(msg)
    return ret


def weather_map_url(appid: str, lat: str, lon: str) -> str:
    """weather_map_urlを作る"""
    return (
        'https://map.yahooapis.jp/map/V1/static?' +
        'appid={}&lat={}&lon={}&z=12&height=640&width=800&overlay=type:rainfall|datelabel:off'
    ).format(appid, lat, lon)


def amesh(client: BaseClient):
    """東京の天気を表示する"""

    user = client.get_send_user_name()
    logger.debug("%s called 'hato amesh'", user)
    client.post('東京の雨雲状況をお知らせするっぽ！')

    url = weather_map_url(conf.YAHOO_API_TOKEN, '35.698856', '139.73091159273')
    req = requests.get(url, stream=True)
    f_name = "amesh.jpg"
    if req.status_code == 200:
        with open(f_name, 'wb') as weather_map_file:
            weather_map_file.write(req.content)
            client.upload(file=f_name, filename="amesh.png")

    if os.path.exists(f_name):
        os.remove(f_name)


def amesh_with_gis(place: str):
    """位置を指定したameshを表示する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'hato amesh '", user)
        client.post('雨雲状況をお知らせするっぽ！')
        lat, lon = split_command(place, 2)

        url = weather_map_url(conf.YAHOO_API_TOKEN, lat, lon)
        req = requests.get(url, stream=True)
        f_name = "amesh.jpg"
        if req.status_code == 200:
            with open(f_name, 'wb') as weather_map_file:
                weather_map_file.write(req.content)
                client.upload(file=f_name, filename="amesh.png")

        os.remove(f_name)
    return ret


def version(client: BaseClient):
    """versionを表示する"""

    user = client.get_send_user_name()
    logger.debug("%s called 'hato version'", user)
    str_ver = "バージョン情報\n```"\
        "Version {}\n"\
        "Copyright (C) 2020 hato-bot Development team\n"\
        "https://github.com/nakkaa/hato-bot ```".format(VERSION)
    client.post(str_ver)
