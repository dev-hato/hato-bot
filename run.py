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
from typing import Callable

slack_events_adapter = SlackEventAdapter(
    conf.SLACK_SIGNING_SECRET, endpoint="/slack/events")

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
    print(message)
    if re.match(hato.respond_to_with_space('^help'), message):
        return hato.help_message
    else:
        return hato.no_action


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    message = event_data["event"]["text"]
    channel = event_data["event"]["channel"]
    user = event_data["event"]["user"]

    analyze_message(message.replace('<@'+user+'>', '').strip()
                    )(SlackClient(channel, user))

    print(message)


slack_events_adapter.start(host='0.0.0.0', port=conf.PORT)
