"""
メッセージを解析する
"""

from typing import Callable

from library.clientclass import BaseClient
import plugins.hato as hato


def analyze_message(message: str) -> Callable[[BaseClient], None]:
    """コマンド解析"""

    conditions = {'help': lambda m: hato.help_message,
                  'eq': lambda m: hato.earth_quake,
                  '地震': lambda m: hato.earth_quake,
                  'text list': lambda m: hato.get_text_list,
                  'text add ': lambda m: hato.add_text(m[len('text add '):]),
                  'text show ': lambda m: hato.show_text(m[len('text show '):]),
                  'text delete ': lambda m: hato.delete_text(m[len('text delete '):]),
                  'text random': lambda m: hato.show_random_text,
                  'text': lambda m: hato.show_random_text,
                  '>< ': lambda m: hato.totuzensi(m[len('>< '):]),
                  'amesh': lambda m: hato.amesh((m[len('amesh'):]).strip()),
                  '標高': lambda m: hato.altitude((m[len('標高'):]).strip()),
                  'version': lambda m: hato.version,
                  'にゃーん': lambda m: hato.yoshiyoshi,
                  }

    for key, method in conditions.items():
        if message.startswith(key):
            return method(message)
    return hato.default_action
