# coding: utf-8

"""
BotのMain関数
"""
import sys
import logging
import logging.config
from slackeventsapi import SlackEventAdapter
import slackbot_settings as conf
import re
from slack import WebClient
import plugins.hato as hato


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


class SlackClient:
    def __init__(self, channel, send_user):
        self.client = WebClient(token=conf.SLACK_API_TOKEN)
        self.slack_channel = channel
        self.send_user = send_user

    def send(self, message):
        self.client.chat_postEphemeral(
            channel=self.slack_channel,
            user="hato",
            text=message
        )

    def get_send_user(self):
        return self.send_user

    def type(self):
        return 'slack'


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    message_raw = event_data["event"]["text"]
    channel = event_data["event"]["channel"]
    user = event_data["event"]["user"]

    space = ' '
    message = message_raw.replace('^', f'^{space}').replace(space, r'\s*')

    if re.match('^help', message):
        hato.help_message(SlackClient(channel, user))

    print(message)


slack_events_adapter.start(host='0.0.0.0', port=conf.PORT)
