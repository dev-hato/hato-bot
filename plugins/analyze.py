"""
メッセージを解析する
"""

from functools import partial
from typing import Callable, List

from library.clientclass import BaseClient, SlackClient
from plugins import hato


def analyze_slack_message(messages: List[dict]) -> Callable[[SlackClient], None]:
    """Slackコマンド解析"""

    message = "".join([m["text"] for m in messages if "text" in m]).strip()
    return analyze_message(message)


def analyze_message(message: str) -> Callable[[BaseClient], None]:
    """コマンド解析"""

    for key, method in hato.conditions.items():
        if message.startswith(key):
            return method(message)
    return partial(hato.default_action, message=message)
