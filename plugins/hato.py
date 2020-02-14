# coding: utf-8
import os
from logging import getLogger
from PIL import Image
import datetime
from slackbot.bot import respond_to, listen_to, default_reply
from library.weather import get_city_id_from_city_name, get_weather
from library.amesh import get_map
from library.labotter import labo_in, labo_rida
from library.vocabularydb import get_vocabularys, add_vocabulary, show_vocabulary, delete_vocabulary
from library.earthquake import generate_quake_info_for_slack, get_quake_list
from library.hukidasi import generator

logger = getLogger(__name__)
VERSION = "0.3.2"

# 「hato help」を見つけたら、使い方を表示する
@respond_to('^help')
def help(message):
    user = message.user['name']
    logger.debug("%s called 'hato help'", user)
    str_help = '\n使い方\n'\
        '```'\
        '天気 [text] ... 地名の天気予報を表示する。\n'\
        'amesh ... ameshを表示する。\n'\
        '地震 ... 最新の地震情報を3件表示する。\n'\
        'text list ... パワーワード一覧を表示する。 \n'\
        'text show [int] ... 指定した番号[int]のパワーワードを表示する。 \n'\
        'text add [text] ... パワーワードに[text]を登録する。 \n'\
        'in ... らぼいんする\n'\
        'rida ... らぼいんからの経過時間を表示する\n'\
        '>< [text] ... 文字列[text]を吹き出しで表示する。\n'\
        'version ... バージョン情報を表示する。\n'\
        '\n詳細はドキュメント(https://github.com/nakkaa/hato-bot/wiki)も見てくれっぽ!```\n'
    message.send(str_help)

@respond_to('^eq$|^地震$')
def earth_quake(message):
    msg = "地震情報を取得できなかったっぽ!"
    result, data = get_quake_list()
    if result:
        msg = "地震情報を取得したっぽ!\n"
        msg = msg + generate_quake_info_for_slack(data, 3)
    message.send(msg)

@respond_to('^in$')
def labotter_in(message):
    msg = "らぼいんに失敗したっぽ!(既に入っているかもしれないっぽ)"
    user_id = message.user['id']
    flag, start_time = labo_in(user_id)
    if flag:
        msg = "らぼいんしたっぽ! \nいん時刻: {}".format(start_time)
    message.send(msg)

@respond_to('^rida$')
def labotter_rida(message):
    msg = "らぼりだに失敗したっぽ!"
    user_id = message.user['id']
    flag, end_time, dt, sum = labo_rida(user_id)
    diff_time = datetime.timedelta(seconds=dt)
    sum_time = datetime.timedelta(seconds=sum)
    if flag:
        msg = "らぼりだしたっぽ! お疲れ様っぽ!\nりだ時刻: {} \n拘束時間: {}\n累計時間: {}".format(end_time, diff_time, sum_time)
    message.send(msg)

@respond_to('^text list$')
def get_text_list(message):
    user = message.user['name']
    logger.debug("%s called 'text list'", user)
    msg = get_vocabularys()
    message.send(msg)

@respond_to('^text add .+')
def add_text(message):
    user = message.user['name']
    logger.debug("%s called 'text add'", user)
    text = message.body['text']
    tmp, tmp2, word = text.split(' ', 2)
    add_vocabulary(word)
    message.send("覚えたっぽ!")

@respond_to('^text show .+')
def add_text(message):
    user = message.user['name']
    logger.debug("%s called 'text show'", user)
    text = message.body['text']
    tmp, tmp2, id = text.split(' ', 2)
    msg = show_vocabulary(int(id))
    message.send(msg)

@respond_to('^text delete .+')
def add_text(message):
    user = message.user['name']
    logger.debug("%s called 'text delete'", user)
    text = message.body['text']
    tmp, tmp2, id = text.split(' ', 2)
    msg = delete_vocabulary(int(id))
    message.send(msg)

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
    logger.debug("%s called 'hato amesh'", user)
    message.send('東京の雨雲状況をお知らせするっぽ！(ちょっと時間かかるっぽ!)')
    # amesh画像を取得する
    file = get_map()

    message.channel.upload_file("amesh", file)

@respond_to('^version')
def version(message):
    user = message.user['name']
    logger.debug("%s called 'hato version'", user)
    str_ver = "バージョン情報\n```"\
        "Version {}\n"\
        "Copyright (C) 2020 hato-bot Develop team\n"\
        "https://github.com/nakkaa/hato-bot ```".format(VERSION)
    message.send(str_ver)
