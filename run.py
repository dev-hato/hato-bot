# coding: utf-8

"""
BotのMain関数
"""
import sys
import logging
import logging.config
from typing import Callable, List
from concurrent.futures import ThreadPoolExecutor
from slackeventsapi import SlackEventAdapter
import slackbot_settings as conf
import plugins.hato as hato
from library.clientclass import SlackClient, BaseClient


slack_events_adapter = SlackEventAdapter(
    conf.SLACK_SIGNING_SECRET, endpoint="/slack/events")


def __init__():
    log_format_config = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout,
    }
    logging.basicConfig(**log_format_config)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)


def analyze_message(message: str) -> Callable[[BaseClient], None]:
    """コマンド解析"""

    conditions = {'help': lambda m: hato.help_message,
                  'eq': lambda m: hato.earth_quake,
                  '地震': lambda m: hato.earth_quake,
                  'in': lambda m: hato.labotter_in,
                  'rida': lambda m: hato.labotter_rida,
                  'text list': lambda m: hato.get_text_list,
                  'text add ': lambda m: hato.add_text(m[len('text add '):]),
                  'text show ': lambda m: hato.show_text(m[len('text show '):]),
                  'text delete ': lambda m: hato.delete_text(m[len('text delete '):]),
                  'text random': lambda m: hato.show_random_text,
                  'text': lambda m: hato.show_random_text,
                  '天気': lambda m: hato.weather((m[len('天気'):]).strip()),
                  '>< ': lambda m: hato.totuzensi(m[len('>< '):]),
                  'amesh': lambda m: hato.amesh,
                  'amesh ': lambda m: hato.amesh_with_gis((m[len('amesh '):]).strip()),
                  'version': lambda m: hato.version,
                  }

    for key, method in conditions.items():
        if message.startswith(key):
            return method(message)
    return hato.default_action


def analyze_slack_message(messages: List[dict]) -> Callable[[SlackClient], None]:
    """Slackコマンド解析"""

    if len(messages) > 0 and messages[0]['type'] == 'text':
        message = messages[0]['text'].strip()
        return analyze_message(message)

    return hato.default_action


TPE = ThreadPoolExecutor(max_workers=3)


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    channel = event_data["event"]["channel"]
    blocks = event_data['event']['blocks']
    authed_users = event_data['authed_users']

    for block in blocks:
        if block['type'] == 'rich_text':
            block_elements = block['elements']
            for block_element in block_elements:
                if block_element['type'] == 'rich_text_section':
                    block_element_elements = block_element['elements']
                    if len(block_element_elements) > 0 and \
                            block_element_elements[0]['type'] == 'user' and \
                        block_element_elements[0]['user_id'] in authed_users:
                        TPE.submit(analyze_slack_message(block_element_elements[1:]), SlackClient(
                            channel, block_element_elements[0]['user_id']))

    print(event_data)


slack_events_adapter.start(host='0.0.0.0', port=conf.PORT)
