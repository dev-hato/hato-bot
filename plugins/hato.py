# coding: utf-8

"""hatobotのチャット部分"""

import imghdr
import json
import os
import re
from enum import Enum, auto
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import requests
from git import Repo
from git.exc import GitCommandNotFound, InvalidGitRepositoryError

import slackbot_settings as conf
from library.clientclass import BaseClient
from library.earthquake import generate_quake_info_for_slack, get_quake_list
from library.geo import get_geo_data
from library.hatokaraage import hato_ha_karaage
from library.hukidasi import generator
from library.jma_amedas import get_jma_amedas
from library.jma_amesh import jma_amesh
from library.omikuji import OmikujiResult, OmikujiResults
from library.omikuji import draw as omikuji_draw
from library.vocabularydb import (
    add_vocabulary,
    delete_vocabulary,
    get_vocabularys,
    show_random_vocabulary,
    show_vocabulary,
)

logger = getLogger(__name__)


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

    str_help = [
        "",
        "使い方",
        "```",
        "amesh ... 東京のamesh(雨雲情報)を表示する。",
        "amesh [text] ... 指定した地名・住所・郵便番号[text]のamesh(雨雲情報)を表示する。",
        "amesh [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])のameshを表示する。",
        "amedas ... 東京のamedas(気象情報)を表示する。",
        "amedas [text] ... 指定した地名・住所・郵便番号[text]のamedas(気象情報)を表示する。",
        "amedas [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])のamedas(気象情報)を表示する。",
        "電力 ... 東京電力管内の電力使用率を表示する。",
        "標高 ... 東京の標高を表示する。",
        "標高 [text] ... 指定した地名・住所・郵便番号[text]の標高を表示する。",
        "標高 [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])の標高を表示する。",
        "eq ... 最新の地震情報を3件表示する。",
        "text list ... パワーワード一覧を表示する。 ",
        "text random ... パワーワードをひとつ、ランダムで表示する。 ",
        "text show [int] ... 指定した番号[int]のパワーワードを表示する。 ",
        "text add [text] ... パワーワードに[text]を登録する。 ",
        "text delete [int] ... 指定した番号[int]のパワーワードを削除する。 ",
        ">< [text] ... 文字列[text]を吹き出しで表示する。",
        "にゃーん ... 「よしよし」と返す。",
        "おみくじ ... おみくじを引いて返す。",
        "version ... バージョン情報を表示する。",
        "",
        "詳細はドキュメント(https://github.com/dev-hato/hato-bot/wiki)も見てくれっぽ!",
        "```",
    ]
    return os.linesep.join(str_help)


@action("default")
def default_action():
    """どのコマンドにもマッチしなかった"""

    return conf.DEFAULT_REPLY


@action("eq")
def earth_quake():
    """地震 地震情報を取得する"""

    msg = "地震情報を取得できなかったっぽ!"
    data = get_quake_list()
    if data is not None:
        msg = "地震情報を取得したっぽ!\n"
        msg = msg + generate_quake_info_for_slack(data, 3)

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
    return "```" + msg + "```"


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
        ext = imghdr.what(weather_map_file.name)

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
        lat, lon = place_list
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

    res = [f"{amedas_data['datetime']}現在の{amedas_data['place']}の気象状況をお知らせするっぽ！", "```"]

    if "temp" in amedas_data:
        res.append(f"気温: {amedas_data['temp'][0]}℃")

    if "precipitation1h" in amedas_data:
        res.append(f"降水量 (前1時間): {amedas_data['precipitation1h'][0]}mm")

    if "windDirection" in amedas_data:
        directions = [
            "北北東",
            "北東",
            "東北東",
            "東",
            "東南東",
            "南東",
            "南南東",
            "南",
            "南南西",
            "南西",
            "西南西",
            "西",
            "西北西",
            "北西",
            "北北西",
            "北",
        ]
        res.append(f"風向: {directions[amedas_data['windDirection'][0] - 1]}")

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
        f"東京電力管内の電力使用率をお知らせするっぽ！\n" f"{latest_data.index[-1]}時点 {latest_data[-1]}%"
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

    str_ver = "バージョン情報\n```" f"Version {conf.VERSION}"

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
        "Copyright (C) 2022 hato-bot Development team\n"
        "https://github.com/dev-hato/hato-bot ```"
    )
    return str_ver


@action("にゃーん")
def yoshiyoshi():
    """「にゃーん」を見つけたら、「よしよし」と返す"""
    return "よしよし"


# 以下おみくじの設定
# Refer: dev-hato/hato-bot#876
class OmikujiEnum(Enum):
    """
    おみくじの結果一覧
    """

    DAI_KICHI = auto()
    CHU_KICHI = auto()
    SHO_KICHI = auto()
    KICHI = auto()
    SUE_KICHI = auto()
    AGE_KICHI = auto()
    KYO = auto()
    DAI_KYO = auto()


omikuji_results = OmikujiResults(
    {
        OmikujiEnum.DAI_KICHI: OmikujiResult(12, ":tada: 大吉 何でもうまくいく!!気がする!!"),
        OmikujiEnum.KICHI: OmikujiResult(100, ":smirk: 吉 まあうまくいくかも!?"),
        OmikujiEnum.CHU_KICHI: OmikujiResult(100, ":smile: 中吉 そこそこうまくいくかも!?"),
        OmikujiEnum.SHO_KICHI: OmikujiResult(100, ":smiley: 小吉 なんとなくうまくいくかも!?"),
        OmikujiEnum.SUE_KICHI: OmikujiResult(
            37, ":expressionless: 末吉 まあ多分うまくいくかもね……!?"
        ),
        OmikujiEnum.AGE_KICHI: OmikujiResult(2, ":poultry_leg: 揚げ吉 鳩を揚げると良いことあるよ!!"),
        OmikujiEnum.KYO: OmikujiResult(12, ":cry: 凶 ちょっと慎重にいったほうがいいかも……"),
        OmikujiEnum.DAI_KYO: OmikujiResult(
            2, ":crying_cat_face: 大凶 そういう時もあります……猫になって耐えましょう"
        ),
    }
)


@action("おみくじ")
def omikuji():
    """
    おみくじ結果を返す
    """

    return omikuji_draw(omikuji_results)[1].message
