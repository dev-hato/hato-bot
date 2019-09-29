# coding: utf-8
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
import unicodedata
from logging import getLogger
logger = getLogger(__name__)

# 「hato help」を見つけたら、使い方を表示する
@listen_to('hato help')
def help(message):
    user = message.user['name']
    logger.debug("%s called 'hato help'", user)
    message.send(
        '\n使い方\n'
        '```'
        'hato help       botの使い方を表示する。\n'
        'hato >< [文字列] 文字列を吹き出しで表示する。\n'
        '```')

# 「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する
@listen_to('^hato &gt;&lt; .+')
def totuzensi(message):
    user = message.user['name']
    text = message.body['text']
    word_list = text.split(' ', 2)
    word = str(word_list[2])
    logger.debug("%s called 'hato >< %s'", user, word)
    word = generator(word)
    msg = '\n```' + word + '```'
    message.send(msg)
    
# 突然の死で使う関数
# Todo: 別ファイルに移したい。
def text_len(text):
    count = 0
    for c in text:
        count += 2 if unicodedata.east_asian_width(c) in 'FWA' else 1
    return count

def generator(msg):
    length = text_len(msg)
    generating = '＿人'
    for i in range(length//2):
        generating += '人'
    generating += '人＿\n＞  ' + msg + '  ＜\n￣^Y'
    for i in range(length//2):
        generating += '^Y'
    generating += '^Y￣'
    return generating
