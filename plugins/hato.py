# coding: utf-8

from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ

@listen_to('hato help')
def listen_func(message):
    #message.send('誰かがリッスンと投稿したようだ')      # ただの投稿
    message.reply(
        '\n使い方\n'
        '```'
        'hato help       botの使い方を表示する。\n'
        'hato >< [文字列] 吹き出しで表示する。\n'
        '```')