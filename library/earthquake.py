# coding: utf-8

import requests
import json

def get_quake_list(limit=10):
    flag = False
    data = None
    quake_url = 'https://api.p2pquake.net/v1/human-readable?limit={}'.format(limit)
    response = requests.get(quake_url)
    if response.status_code == 200:
        flag = True
        data = json.loads(response.text)
        return flag, data
    else:
        return flag, data

def generate_quake_info_for_slack(data, max_cnt=1):
    cnt = 1
    msg = '```'
    for row in data:
        code = row['code']
        if code == 551: # 551は地震情報 https://www.p2pquake.net/dev/json-api/#i-6
            time = row['earthquake']['time']
            singenti = row['earthquake']['hypocenter']['name']
            magnitude = row['earthquake']['hypocenter']['magnitude']
            sindo = row['earthquake']['maxScale']

            if sindo is None:
                sindo = ''
            else:
                sindo /= 10

            msg = msg + '\n---\n発生時刻: {}\n震源地: {}\nマグニチュード: {}\n最大震度: {}'.format(time, singenti, magnitude, sindo)
            if max_cnt <= cnt:
                break
            cnt += 1
    msg = msg + '\n\n出典: https://www.p2pquake.net/dev/json-api/ \n気象庁HP: https://www.jma.go.jp/jp/quake/```'
    return msg
