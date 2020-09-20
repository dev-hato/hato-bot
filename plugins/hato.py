# coding: utf-8

"""hatobotのチャット部分"""

import imghdr
import json
import os
import re
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import List
import requests
from git import Repo
from git.exc import InvalidGitRepositoryError

import slackbot_settings as conf
from library.vocabularydb \
    import get_vocabularys, add_vocabulary, show_vocabulary, delete_vocabulary, show_random_vocabulary
from library.earthquake import generate_quake_info_for_slack, get_quake_list
from library.hukidasi import generator
from library.geo import get_geo_data
from library.hatokaraage import hato_ha_karaage
from library.clientclass import BaseClient

logger = getLogger(__name__)
VERSION = "2.0.1"


def split_command(command: str, maxsplit: int = 0) -> List[str]:
    """コマンドを分離する"""

    return re.split(r'\s+', command.strip().strip('　'), maxsplit)


def help_message(client: BaseClient):
    """「hato help」を見つけたら、使い方を表示する"""

    logger.debug("%s called 'hato help'", client.get_send_user())
    logger.debug("%s app called 'hato help'", client.get_type())
    str_help = '\n使い方\n' \
               '```' \
               'amesh ... 東京のameshを表示する。\n' \
               'amesh [text] ... 指定した地名・住所[text]のameshを表示する。\n' \
               'amesh [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])のameshを表示する。\n' \
               '標高 ... 東京の標高を表示する。\n' \
               '標高 [text] ... 指定した地名・住所[text]の標高を表示する。\n' \
               '標高 [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])の標高を表示する。\n' \
               'eq ... 最新の地震情報を3件表示する。\n' \
               'text list ... パワーワード一覧を表示する。 \n' \
               'text random ... パワーワードをひとつ、ランダムで表示する。 \n' \
               'text show [int] ... 指定した番号[int]のパワーワードを表示する。 \n' \
               'text add [text] ... パワーワードに[text]を登録する。 \n' \
               'text delete [int] ... 指定した番号[int]のパワーワードを削除する。 \n' \
               '>< [text] ... 文字列[text]を吹き出しで表示する。\n' \
               'version ... バージョン情報を表示する。\n' \
               '\n詳細はドキュメント(https://github.com/dev-hato/hato-bot/wiki)も見てくれっぽ!```\n'
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


def totuzensi(message: str):
    """「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        word = hato_ha_karaage(message)
        logger.debug("%s called 'hato >< %s'", user, word)
        msg = generator(word)
        client.post('```' + msg + '```')
    return ret


def amesh(place: str):
    """天気を表示する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'hato amesh '", user)
        msg: str = '雨雲状況をお知らせするっぽ！'
        lat = None
        lon = None
        place_list = split_command(place, 2)

        if len(place_list) == 2:
            lat, lon = place_list
        else:
            geo_data = get_geo_data(place_list[0] or '東京')
            if geo_data is not None:
                msg = geo_data['place'] + 'の' + msg
                lat = geo_data['lat']
                lon = geo_data['lon']

        if lat is None or lon is None:
            client.post('雨雲状況を取得できなかったっぽ......')
            return None

        client.post(msg)
        req = requests.get('https://map.yahooapis.jp/map/V1/static',
                           {
                               'appid': conf.YAHOO_API_TOKEN,
                               'lat': lat,
                               'lon': lon,
                               'z': '12',
                               'height': '640',
                               'width': '800',
                               'overlay': 'type:rainfall|datelabel:off'
                           },
                           stream=True)
        if req.status_code == 200:
            with NamedTemporaryFile() as weather_map_file:
                weather_map_file.write(req.content)
                filename = ['amesh']
                ext = imghdr.what(weather_map_file.name)

                if ext:
                    filename.append(ext)

                client.upload(file=weather_map_file.name,
                              filename=os.path.extsep.join(filename))

        return req

    return ret


def altitude(place: str):
    """標高を表示する"""

    def ret(client: BaseClient):
        user = client.get_send_user_name()
        logger.debug("%s called 'hato altitude '", user)
        coordinates = None
        place_name = None
        place_list = split_command(place, 2)

        if len(place_list) == 2:
            try:
                coordinates = [str(float(p)) for p in reversed(place_list)]
            except ValueError:
                client.post('引数が正しくないっぽ......')
                return None

            place_name = ', '.join(reversed(coordinates))
        else:
            geo_data = get_geo_data(place_list[0] or '東京')
            if geo_data is not None:
                coordinates = [geo_data['lon'], geo_data['lat']]
                place_name = geo_data['place']

        if coordinates is not None:
            res = requests.get('https://map.yahooapis.jp/alt/V1/getAltitude',
                               {
                                   'appid': conf.YAHOO_API_TOKEN,
                                   'coordinates': ','.join(coordinates),
                                   'output': 'json'
                               },
                               stream=True)
            if res.status_code == 200:
                data_list = json.loads(res.content)
                if 'Feature' in data_list:
                    for data in data_list['Feature']:
                        if 'Property' in data and 'Altitude' in data['Property']:
                            altitude_ = data['Property']['Altitude']
                            altitude_str = '{:,}'.format(altitude_)
                            client.post(f'{place_name}の標高は{altitude_str}mっぽ！')
                            return res

        client.post('標高を取得できなかったっぽ......')
        return None

    return ret


def version(client: BaseClient):
    """versionを表示する"""

    user = client.get_send_user_name()
    logger.debug("%s called 'hato version'", user)
    str_ver = "バージョン情報\n```" \
              f"Version {VERSION}"

    if conf.GIT_COMMIT_HASH:
        str_ver += f" (Commit {conf.GIT_COMMIT_HASH[:7]})"
    else:
        try:
            repo = Repo()
            str_ver += f" (Commit {repo.head.commit.hexsha[:7]})"
        except InvalidGitRepositoryError:
            pass

    str_ver += "\n" \
               "Copyright (C) 2020 hato-bot Development team\n" \
               "https://github.com/dev-hato/hato-bot ```"
    client.post(str_ver)
