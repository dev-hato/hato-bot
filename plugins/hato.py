# coding: utf-8

"""hatobotのチャット部分"""

import json
import os
import re
from functools import partial
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import puremagic
import requests
from git import Repo
from git.exc import GitCommandNotFound, InvalidGitRepositoryError

import slackbot_settings as conf
from library.chat_gpt import chat_gpt, image_create
from library.clientclass import BaseClient
from library.earthquake import generate_map_img, get_quake_list
from library.geo import get_geo_data
from library.hatokaraage import hato_ha_karaage
from library.hukidasi import generator
from library.jma_amedas import get_jma_amedas
from library.jma_amesh import jma_amesh
from library.textlint import get_textlint_result
from library.vocabularydb import (
    add_vocabulary,
    delete_vocabulary,
    get_vocabularys,
    show_random_vocabulary,
    show_vocabulary,
)
from plugins.hato_mikuji import HatoMikuji

logger = getLogger(__name__)

conditions = {
    "help": lambda m: help_message,
    "eq": lambda m: partial(earth_quake),
    "地震": lambda m: partial(earth_quake),
    "textlint": lambda m: partial(textlint, text=m[len("textlint ") :]),
    "text list": lambda m: get_text_list,
    "text add ": lambda m: partial(add_text, word=m[len("text add ") :]),
    "text show ": lambda m: partial(show_text, power_word_id=m[len("text show ") :]),
    "text delete ": lambda m: partial(
        delete_text, power_word_id=m[len("text delete ") :]
    ),
    "text random": lambda m: show_random_text,
    "text": lambda m: show_random_text,
    ">< ": lambda m: partial(totuzensi, message=m[len(">< ") :]),
    "amesh": lambda m: partial(amesh, place=m[len("amesh") :].strip()),
    "amedas": lambda m: partial(amedas, place=m[len("amedas") :].strip()),
    "電力": lambda m: electricity_demand,
    "標高": lambda m: partial(altitude, place=m[len("標高") :].strip()),
    "version": lambda m: version,
    "にゃーん": lambda m: yoshiyoshi,
    "おみくじ": lambda m: omikuji,
    "chat": lambda m: partial(chat, message=m[len("chat") :].strip()),
    "画像生成": lambda m: partial(image_generate, message=m[len("画像生成") :].strip()),
    "ping": lambda m: ping,
}


def action(plugin_name: str, with_client: bool = False):
    """
    アクション定義メソッドに使うデコレータ

    """

    def _action(func):
        def wrapper(client: BaseClient, *args, **kwargs):
            logger.debug("%s called '%s'", client.get_send_user(), plugin_name)
            logger.debug("%s app called '%s'", client.get_type(), plugin_name)
            if with_client:
                func(client, *args, **kwargs)
            else:
                return_val = func(*args, **kwargs)
                if isinstance(return_val, str):
                    client.post(return_val)

        return wrapper

    return _action


def split_command(command: str, maxsplit: int = 0) -> List[str]:
    """コマンドを分離する"""

    return re.split(r"\s+", command.strip().strip("　"), maxsplit)


@action("help")
def help_message():
    """「hato help」を見つけたら、使い方を表示する"""

    with open("commands.txt", "r") as f:
        str_help = [
            "",
            "使い方",
            "```",
            f.read().strip(),
            "",
            "詳細はドキュメント(https://github.com/dev-hato/hato-bot/wiki)も見てくれっぽ!",
            "```",
        ]
        return os.linesep.join(str_help)


@action("default", with_client=True)
def default_action(client: BaseClient, message: str):
    """どのコマンドにもマッチしなかった"""

    try:
        conditions["chat"](message)(client=client)
    except Exception as e:
        logger.exception(e)
        client.post(conf.DEFAULT_REPLY)


@action("eq", with_client=True)
def earth_quake(client: BaseClient):
    """地震 地震情報を取得する"""

    msg: str = "地震情報を取得できなかったっぽ!"
    data = get_quake_list(3)

    if data is None:
        client.post(msg)
        return

    msg = "地震情報を取得したっぽ!\n"
    msg += "```\n"
    msg += "出典: https://www.p2pquake.net/json_api_v2/ \n"
    msg += "気象庁HP: https://www.jma.go.jp/jp/quake/\n"
    msg += "```"
    client.post(msg)

    for row in data:
        time = row["earthquake"]["time"]
        hypocenter = row["earthquake"]["hypocenter"]["name"]
        magnitude = row["earthquake"]["hypocenter"]["magnitude"]
        earthquake_intensity = row["earthquake"]["maxScale"]

        # 震源情報が存在しない場合は-1になる
        # https://www.p2pquake.net/json_api_v2/#/P2P%E5%9C%B0%E9%9C%87%E6%83%85%E5%A0%B1%20API/get_history
        if earthquake_intensity == -1:
            earthquake_intensity = ""
        else:
            earthquake_intensity /= 10
            earthquake_intensity = str(earthquake_intensity)

        msg = "```\n"
        msg += f"発生時刻: {time}\n"
        msg += f"震源地: {hypocenter}\n"
        msg += f"マグニチュード: {magnitude}\n"
        msg += f"最大震度: {earthquake_intensity}\n"
        msg += "```"
        client.post(msg)

        lat = row["earthquake"]["hypocenter"]["latitude"]
        lng = row["earthquake"]["hypocenter"]["longitude"]

        # 震源情報が存在しない場合は-200になる
        # https://www.p2pquake.net/json_api_v2/#/P2P%E5%9C%B0%E9%9C%87%E6%83%85%E5%A0%B1%20API/get_history
        if -200 < lat and -200 < lng:
            map_img = generate_map_img(
                lat=float(lat),
                lng=float(lng),
                zoom=10,
                around_tiles=2,
                time=time,
                hypocenter=hypocenter,
                magnitude=magnitude,
                earthquake_intensity=earthquake_intensity,
            )
            with NamedTemporaryFile() as map_file:
                map_img.save(map_file, format="PNG")

                filename = ["map"]
                ext = puremagic.what(map_file.name)

                if ext:
                    filename.append(ext)

                client.upload(
                    file=map_file.name, filename=os.path.extsep.join(filename)
                )


@action("textlint")
def textlint(text: str):
    """文章を校正する"""

    msg = "完璧な文章っぽ!"
    res = get_textlint_result(text)

    if res:
        msg = "文章の修正点をリストアップしたっぽ!\n" + res

    return msg


@action("text list")
def get_text_list():
    """パワーワードのリストを表示"""

    return get_vocabularys()


@action("text add")
def add_text(word: str):
    """パワーワードの追加"""

    add_vocabulary(word)
    return "覚えたっぽ!"


@action("text show")
def show_text(power_word_id: str):
    """指定した番号のパワーワードを表示する"""

    return show_vocabulary(int(power_word_id))


@action("text random")
def show_random_text():
    """パワーワードの一覧からランダムで1つを表示する"""

    return show_random_vocabulary()


@action("text delete")
def delete_text(power_word_id: str):
    """指定した番号のパワーワードを削除する"""

    return delete_vocabulary(int(power_word_id))


@action("><")
def totuzensi(message: str):
    """「hato >< 文字列」を見つけたら、文字列を突然の死で装飾する"""

    word = hato_ha_karaage(message)
    msg = generator(word)
    return "```\n" + msg + "\n```"


@action("amesh", with_client=True)
def amesh(client: BaseClient, place: str):
    """天気を表示する"""

    msg: str = "雨雲状況をお知らせするっぽ！"
    lat = None
    lon = None
    place_list = split_command(place, 2)

    if len(place_list) == 2:
        lat, lon = place_list
    else:
        geo_data = get_geo_data(place_list[0] or "東京")
        if geo_data is not None:
            msg = geo_data["place"] + "の" + msg
            lat = geo_data["lat"]
            lon = geo_data["lon"]

    if lat is None or lon is None:
        client.post("座標を特定できなかったっぽ......")
        return

    client.post(msg)
    amesh_img = jma_amesh(lat=float(lat), lng=float(lon), zoom=10, around_tiles=2)
    if amesh_img is None:
        client.post("雨雲状況を取得できなかったっぽ......")
        return

    with NamedTemporaryFile() as weather_map_file:
        amesh_img.save(weather_map_file, format="PNG")

        filename = ["amesh"]
        ext = puremagic.what(weather_map_file.name)

        if ext:
            filename.append(ext)

        client.upload(
            file=weather_map_file.name, filename=os.path.extsep.join(filename)
        )


@action("amedas", with_client=True)
def amedas(client: BaseClient, place: str):
    """気象情報を表示する"""

    lat: Optional[float] = None
    lon: Optional[float] = None
    place_list = split_command(place, 2)

    if len(place_list) == 2:
        lat = float(place_list[0])
        lon = float(place_list[1])
    else:
        geo_data = get_geo_data(place_list[0] or "東京")
        if geo_data is not None:
            lat = float(geo_data["lat"])
            lon = float(geo_data["lon"])

    if lat is None or lon is None:
        client.post("座標を特定できなかったっぽ......")
        return

    amedas_data = get_jma_amedas(lat, lon)

    if amedas_data is None:
        client.post("気象状況を取得できなかったっぽ......")
        return

    res = [
        f"{amedas_data['datetime']}現在の{amedas_data['place']}の気象状況をお知らせするっぽ！",
        "```",
    ]

    if "temp" in amedas_data:
        res.append(f"気温: 摂氏{amedas_data['temp'][0]}度")

    if "precipitation1h" in amedas_data:
        res.append(f"降水量 (前1時間): {amedas_data['precipitation1h'][0]}mm")

    if "windDirectionJP" in amedas_data:
        res.append(f"風向: {amedas_data['windDirectionJP']}")

    if "wind" in amedas_data:
        res.append(f"風速: {amedas_data['wind'][0]}m/s")

    if "sun1h" in amedas_data:
        res.append(f"日照時間 (前1時間): {amedas_data['sun1h'][0]}時間")

    if "humidity" in amedas_data:
        res.append(f"湿度: {amedas_data['humidity'][0]}%")

    if "normalPressure" in amedas_data:
        res.append(f"海面気圧: {amedas_data['normalPressure'][0]}hPa")

    res.append("```")
    client.post(os.linesep.join(res))


@action("電力", with_client=True)
def electricity_demand(client: BaseClient):
    """東京電力管内の電力使用率を表示する"""
    url = "https://www.tepco.co.jp/forecast/html/images/juyo-d-j.csv"
    res = requests.get(url)

    if res.status_code != 200:
        client.post("東京電力管内の電力使用率を取得できなかったっぽ......")
        return

    res_io = pd.io.stata.BytesIO(res.content)
    df_base = pd.read_csv(res_io, encoding="shift_jis", skiprows=12, index_col="TIME")
    df_percent = df_base[:24]["使用率(%)"].dropna().astype(int)
    latest_data = df_percent[df_percent > 0]
    client.post(
        f"東京電力管内の電力使用率をお知らせするっぽ！\n"
        f"{latest_data.index[-1]}時点 {latest_data[-1]}%"
    )
    df_percent.plot()

    plt.ylim(0, 100)
    plt.grid()

    with NamedTemporaryFile() as graph_file:
        ext = "png"
        plt.savefig(graph_file.name, format=ext)
        client.upload(
            file=graph_file.name,
            filename=os.path.extsep.join(["tepco_electricity_demand_graph", ext]),
        )

    plt.close("all")
    return


@action("標高")
def altitude(place: str):
    """標高を表示する"""

    coordinates = None
    place_name = None
    place_list = split_command(place, 2)

    if len(place_list) == 2:
        try:
            coordinates = [str(float(p)) for p in reversed(place_list)]
        except ValueError:
            return "引数が正しくないっぽ......"

        place_name = ", ".join(reversed(coordinates))
    else:
        geo_data = get_geo_data(place_list[0] or "東京")
        if geo_data is not None:
            coordinates = [geo_data["lon"], geo_data["lat"]]
            place_name = geo_data["place"]

    if coordinates is None:
        return "座標を特定できなかったっぽ......"

    res = requests.get(
        "https://map.yahooapis.jp/alt/V1/getAltitude",
        {
            "appid": conf.YAHOO_API_TOKEN,
            "coordinates": ",".join(coordinates),
            "output": "json",
        },
        stream=True,
    )

    if res.status_code == 200:
        data_list = json.loads(res.content)
        if "Feature" in data_list:
            for data in data_list["Feature"]:
                if "Property" in data and "Altitude" in data["Property"]:
                    altitude_ = data["Property"]["Altitude"]
                    altitude_str = f"{altitude_:,}"
                    return f"{place_name}の標高は{altitude_str}mっぽ！"

    return "標高を取得できなかったっぽ......"


@action("version")
def version():
    """versionを表示する"""

    str_ver = "バージョン情報\n```\n" f"Version {conf.VERSION}"

    if conf.GIT_COMMIT_HASH:
        str_ver += f" (Commit {conf.GIT_COMMIT_HASH[:7]})"
    else:
        try:
            repo = Repo()
            str_ver += f" (Commit {repo.head.commit.hexsha[:7]})"
        except (InvalidGitRepositoryError, GitCommandNotFound):
            pass

    str_ver += (
        "\n"
        "Copyright (C) 2024 hato-bot Development team\n"
        "https://github.com/dev-hato/hato-bot\n```"
    )
    return str_ver


@action("にゃーん")
def yoshiyoshi():
    """「にゃーん」を見つけたら、「よしよし」と返す"""
    return "よしよし"


@action("おみくじ")
def omikuji():
    """
    おみくじ結果を返す
    """

    return HatoMikuji.draw()


@action("chat")
def chat(message: str):
    """
    chat-gptに聞く
    """

    return chat_gpt(message=message)


@action("画像生成", with_client=True)
def image_generate(client: BaseClient, message: str):
    """
    画像生成を行う
    """

    url = image_create(message=message)

    if url is None:
        return "画像を生成できなかったっぽ......"

    """
    urlから画像ファイルをダウンロードして、画像を返す
    """
    with NamedTemporaryFile() as generated_file:
        generated_file.write(requests.get(url).content)
        client.upload(
            file=generated_file.name,
            filename="image.png",
        )


@action("ping")
def ping():
    """「ping」したら「PONG」と返す"""

    return "PONG"
