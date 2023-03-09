"""
メッセージを解析する
"""

from functools import partial
from typing import Callable

from library.clientclass import BaseClient
from plugins import hato


def analyze_message(message: str) -> Callable[[BaseClient], None]:
    """コマンド解析"""

    conditions = {
        "help": lambda m: hato.help_message,
        "eq": lambda m: partial(hato.earth_quake),
        "地震": lambda m: partial(hato.earth_quake),
        "textlint": lambda m: partial(hato.textlint, text=m[len("textlint ") :]),
        "text list": lambda m: hato.get_text_list,
        "text add ": lambda m: partial(hato.add_text, word=m[len("text add ") :]),
        "text show ": lambda m: partial(
            hato.show_text, power_word_id=m[len("text show ") :]
        ),
        "text delete ": lambda m: partial(
            hato.delete_text, power_word_id=m[len("text delete ") :]
        ),
        "text random": lambda m: hato.show_random_text,
        "text": lambda m: hato.show_random_text,
        ">< ": lambda m: partial(hato.totuzensi, message=m[len(">< ") :]),
        "amesh": lambda m: partial(hato.amesh, place=m[len("amesh") :].strip()),
        "amedas": lambda m: partial(hato.amedas, place=m[len("amedas") :].strip()),
        "電力": lambda m: hato.electricity_demand,
        "標高": lambda m: partial(hato.altitude, place=m[len("標高") :].strip()),
        "version": lambda m: hato.version,
        "にゃーん": lambda m: hato.yoshiyoshi,
        "おみくじ": lambda m: hato.omikuji,
        "chat": lambda m: partial(hato.chat, message=m[len("chat") :].strip()),
        "画像生成": lambda m: partial(
            hato.image_generate, message=m[len("画像生成") :].strip()
        ),
    }

    for key, method in conditions.items():
        if message.startswith(key):
            return method(message)
    return hato.default_action
