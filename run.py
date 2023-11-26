# coding: utf-8

"""
BotのMain関数
"""
import asyncio
import json
import logging
import logging.config
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List

import discord
import websockets
from flask import Flask, jsonify, request
from markupsafe import escape
from misskey import Misskey
from requests.exceptions import ReadTimeout
from slackeventsapi import SlackEventAdapter

import slackbot_settings as conf
from library.clientclass import (
    ApiClient,
    DiscordClient,
    MisskeyClient,
    SlackClient,
)
from library.database import Database
from plugins import analyze

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(
    signing_secret=conf.SLACK_SIGNING_SECRET, endpoint="/slack/events", server=app
)


def __init__():
    log_format_config = {
        "format": "[%(asctime)s] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "level": logging.DEBUG,
        "stream": sys.stdout,
    }
    logging.basicConfig(**log_format_config)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
        logging.WARNING
    )


def analyze_slack_message(messages: List[dict]) -> Callable[[SlackClient], None]:
    """Slackコマンド解析"""

    message = "".join([m["text"] for m in messages if "text" in m]).strip()
    return analyze.analyze_message(message)


@slack_events_adapter.on("app_mention")
def on_app_mention(event_data):
    """
    appにメンションが送られたらここが呼ばれる
    """

    channel = event_data["event"]["channel"]
    blocks = event_data["event"]["blocks"]
    authed_users = event_data["authed_users"]
    client_msg_id = event_data["event"]["client_msg_id"]

    print(f"event_data: {event_data}")
    print(f"channel: {channel}")
    print(f"blocks: {blocks}")
    print(f"authed_users: {authed_users}")
    print(f"client_msg_id: {client_msg_id}")

    with Database() as _db, _db.conn.cursor() as cursor:
        cursor.execute(
            "SELECT client_msg_id FROM slack_client_msg_id WHERE client_msg_id = %s LIMIT 1",
            (client_msg_id,),
        )

        if cursor.fetchone():
            print("skip")
            return

        cursor.execute(
            "DELETE FROM slack_client_msg_id "
            "WHERE created_at < CURRENT_TIMESTAMP - interval '10 minutes'",
            (client_msg_id,),
        )
        cursor.execute(
            "INSERT INTO slack_client_msg_id(client_msg_id, created_at) "
            "VALUES(%s, CURRENT_TIMESTAMP)",
            (client_msg_id,),
        )
        _db.conn.commit()

    with ThreadPoolExecutor(max_workers=3) as tpe:
        for block in blocks:
            if block["type"] == "rich_text":
                block_elements = block["elements"]
                for block_element in block_elements:
                    if block_element["type"] == "rich_text_section":
                        block_element_elements = block_element["elements"]
                        if (
                            len(block_element_elements) > 0
                            and block_element_elements[0]["type"] == "user"
                            and block_element_elements[0]["user_id"] in authed_users
                        ):
                            tpe.submit(
                                analyze_slack_message(block_element_elements[1:]),
                                SlackClient(
                                    channel, block_element_elements[0]["user_id"]
                                ),
                            )


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
    msg = request.json["message"]
    channel = request.json["channel"]
    user = request.json["user"]
    client = SlackClient(channel, user)
    client.post(f"コマンド: {msg}")
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
    msg = escape(request.json["message"])
    client = ApiClient()
    client.post(f"コマンド: {msg}")
    analyze.analyze_message(msg)(client)
    return client.response


@app.route("/status", methods=["GET"])
def status():
    """
    死活監視のためのレスポンスをJSON形式で返します
    """
    return jsonify({"message": "hato-bot is running", "version": conf.VERSION}), 200


intents = discord.Intents.all()
discordClient = discord.Client(intents=intents)


@discordClient.event
async def on_message(message):
    if message.author == discordClient.user:
        return

    if discordClient.user in message.mentions:
        async with message.channel.typing():
            await asyncio.get_event_loop().run_in_executor(
                None,
                analyze.analyze_message(
                    # `message.content.replace("\xa0", " ").split(" ", 1)[1]` は、メンション先を除いた文字列
                    message.content.replace("\xa0", " ").split(" ", 1)[1]
                ),
                DiscordClient(discordClient, message),
            )


def main():
    """メイン関数"""

    logger = logging.getLogger(__name__)
    if conf.MODE == "discord":
        discordClient.run(token=conf.DISCORD_API_TOKEN)
    elif conf.MODE == "misskey":
        misskey_client = Misskey(conf.MISSKEY_DOMAIN, i=conf.MISSKEY_API_TOKEN)

        async def misskey_runner():
            while True:
                try:
                    # pylint: disable=E1101
                    async with websockets.connect(
                        "wss://"
                        + misskey_client.address
                        + "/streaming"
                        + "?i="
                        + misskey_client.token
                    ) as ws:
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "connect",
                                    "body": {"channel": "main", "id": "main"},
                                }
                            )
                        )
                        while True:
                            data = json.loads(await ws.recv())
                            if (
                                data["type"] == "channel"
                                and data["body"]["type"] == "mention"
                            ):
                                note = data["body"]["body"]
                                host = note["user"].get("host")
                                mentions = note.get("mentions")
                                if (
                                    host is None or host == conf.MISSKEY_DOMAIN
                                ) and mentions:
                                    cred = None

                                    for i in range(10):
                                        try:
                                            cred = misskey_client.i()
                                            break
                                        except ReadTimeout as e:
                                            logger.exception(e)
                                            time.sleep(1)

                                    if cred is not None and cred["id"] in mentions:
                                        client = MisskeyClient(misskey_client, note)
                                        try:
                                            analyze.analyze_message(
                                                note["text"]
                                                .replace("\xa0", " ")
                                                .split(" ", 1)[1]
                                            )(client)
                                        except Exception as e:
                                            logger.exception(e)
                                            client.post("エラーが発生したっぽ......")
                except websockets.ConnectionClosedError:
                    time.sleep(1)

        asyncio.get_event_loop().run_until_complete(misskey_runner())
    else:
        app.run(host="0.0.0.0", port=conf.PORT)


if __name__ == "__main__":
    main()
