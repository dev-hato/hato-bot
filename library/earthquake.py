# coding: utf-8

"""
地震情報
"""

import json
from typing import Optional, Any
import requests


def get_quake_list(limit: int = 10) -> Optional[Any]:
    """
    地震リストを取得
    """
    quake_url = 'https://api.p2pquake.net/v1/human-readable?limit={}'.format(
        limit)
    response = requests.get(quake_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None


def generate_quake_info_for_slack(data: Any, max_cnt: int = 1) -> str:
    """
    地震情報をslack表示用に加工する
    """
    cnt = 1
    msg: str = '```\n'
    for row in data:
        code = int(row['code'])
        if code == 551:  # 551は地震情報 https://www.p2pquake.net/dev/json-api/#i-6
            time = row['earthquake']['time']
            singenti = row['earthquake']['hypocenter']['name']
            magnitude = row['earthquake']['hypocenter']['magnitude']
            sindo = row['earthquake']['maxScale']

            if sindo is None:
                sindo = ''
            else:
                sindo /= 10

            msg += '---\n'
            msg += '発生時刻: {}\n'.format(time)
            msg += '震源地: {}\n'.format(singenti)
            msg += 'マグニチュード: {}\n'.format(magnitude)
            msg += '最大震度: {}\n\n'.format(sindo)
            if max_cnt <= cnt:
                break
            cnt += 1
    msg += '出典: https://www.p2pquake.net/dev/json-api/ \n'
    msg += '気象庁HP: https://www.jma.go.jp/jp/quake/\n'
    msg += '```\n'
    return msg
