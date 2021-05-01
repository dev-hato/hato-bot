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
from flask import Flask, request, escape
import slackbot_settings as conf
import plugins.hato as hato
import plugins.analyze as analyze
from library.clientclass import SlackClient, ApiClient

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


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    channel = escape(event_data["event"]["channel"])
    blocks = escape(event_data['event']['blocks'])
    authed_users = escape(event_data['authed_users'])

    with ThreadPoolExecutor(max_workers=3) as tpe:
        for block in blocks:
            if block['type'] == 'rich_text':
                block_elements = block['elements']
                for block_element in block_elements:
                    if block_element['type'] == 'rich_text_section':
                        block_element_elements = block_element['elements']
                        if len(block_element_elements) > 0 and \
                                block_element_elements[0]['type'] == 'user' and \
                                block_element_elements[0]['user_id'] in authed_users:
                            tpe.submit(analyze_slack_message(block_element_elements[1:]),
                                       SlackClient(channel,
                                                   block_element_elements[0]['user_id']))

    print(f'event_data: {event_data}')
    print(f'channel: {channel}')
    print(f'blocks: {blocks}')
    print(f'authed_users: {authed_users}')


@app.route("/", methods=["GET", "POST"])
def http_app():
    """
    localでテストできます

    <コマンド例>
    curl -XPOST -d '{"message": "鳩", "channel": "C0123A4B5C6", "user": "U012A34BCDE"}' \
        -H "Content-Type: application/json" http://localhost:3000/

    or

    pipenv run python post_command.py --channel C0123A4B5C6 --user U012A34BCDE "鳩"
    """
    msg = escape(request.json['message'])
    channel = escape(request.json['channel'])
    user = escape(request.json['user'])
    client = SlackClient(channel, user)
    client.post(f'コマンド: {msg}')
    analyze.analyze_message(msg)(client)
    return "success"


@app.route("/healthcheck", methods=["GET", "POST"])
def healthcheck_app():
    """
    api形式で動作確認を行えます
    Slackへの投稿は行われません

    <コマンド例>
    curl -XPOST -d '{"message": "鳩"}' \
        -H "Content-Type: application/json" http://localhost:3000/healthcheck
    """
    msg = escape(request.json['message'])
    client = ApiClient()
    client.post(f'コマンド: {msg}')
    analyze.analyze_message(msg)(client)
    return client.response


def main():
    """メイン関数"""

    app.run(host='0.0.0.0', port=conf.PORT)


if __name__ == "__main__":
    main()
