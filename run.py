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
from flask import Flask
import slackbot_settings as conf
import plugins.hato as hato
import plugins.analyze as analyze
from library.clientclass import SlackClient

app = Flask(__name__)


slack_events_adapter = SlackEventAdapter(
    signing_secret=conf.SLACK_SIGNING_SECRET, endpoint="/slack/events", server=app)


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


def analyze_slack_message(messages: List[dict]) -> Callable[[SlackClient], None]:
    """Slackコマンド解析"""

    if len(messages) > 0 and messages[0]['type'] == 'text':
        message = messages[0]['text'].strip()
        return analyze.analyze_message(message)

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=conf.PORT)
