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
        'help': lambda m: hato.help_message,
        'eq': lambda m: hato.earth_quake,
        '地震': lambda m: hato.earth_quake,
        'text list': lambda m: hato.get_text_list,
        'text add ': lambda m: partial(
            hato.add_text,
            word=m[len('text add '):]
        ),
        'text show ': lambda m: partial(
            hato.show_text,
            power_word_id=m[len('text show '):]
        ),
        'text delete ': lambda m: partial(
            hato.delete_text,
            power_word_id=m[len('text delete '):]
        ),
        'text random': lambda m: hato.show_random_text,
        'text': lambda m: hato.show_random_text,
        '>< ': lambda m: partial(hato.totuzensi, message=m[len('>< '):]),
        'amesh': lambda m: partial(hato.amesh, place=m[len('amesh'):].strip()),
        '電力': lambda m: hato.electricity_demand,
        '標高': lambda m: partial(hato.altitude, place=m[len('標高'):].strip()),
        'version': lambda m: hato.version,
        'にゃーん': lambda m: hato.yoshiyoshi,
        'おみくじ': lambda m: hato.omikuji,
    }

    for key, method in conditions.items():
        if message.startswith(key):
            return method(message)
    return hato.default_action
