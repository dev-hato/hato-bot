# coding: utf-8

"""
BotのMain関数
"""
import sys
import logging
import logging.config
import re
from slackeventsapi import SlackEventAdapter
import slackbot_settings as conf
import plugins.hato as hato
from library.clientclass import SlackClient, BaseClient
from typing import Callable, List

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


def analyze_message(messages: List[any], user_id: str) -> Callable[[BaseClient], None]:
    if len(messages) > 0 and messages[0]['type'] == 'text':
        message = messages[0]['text'].strip()
        if message.startswith('help'):
            return hato.help_message
        if message.startswith('eq') or message.startswith('地震'):
            return hato.earth_quake
        if message.startswith('in'):
            return hato.labotter_in
        if message.startswith('rida'):
            return hato.labotter_rida
        if message.startswith('text list'):
            return hato.get_text_list
        if message.startswith('text add '):
            return hato.add_text(message[len('text add '):])
        if message.startswith('text show '):
            return hato.show_text(message[len('text show '):])
        if message.startswith('text delete '):
            return hato.delete_text(message[len('text delete '):])
        if message.startswith('text random') or message.startswith('text'):
            return hato.show_random_text
        if message.startswith('天気'):
            return hato.weather((message[len('天気'):]).strip())
        if message.startswith('>< '):
            return hato.totuzensi(message[len('>< '):])
        if message.startswith('version'):
            return hato.version

    return hato.default_action


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    channel = event_data["event"]["channel"]
    user = event_data['event']['user']
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
                        analyze_message(block_element_elements[1:], user
                                        )(SlackClient(channel, block_element_elements[0]['user_id']))

    print(event_data)


slack_events_adapter.start(host='0.0.0.0', port=conf.PORT)
