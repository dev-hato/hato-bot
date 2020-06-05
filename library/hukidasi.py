# coding: utf-8

"""
吹き出し用にtextを装飾する
"""

import unicodedata
# Sudden Death(元にしたコードのライセンスは以下の通り)
# MIT License
# Copyright (c) 2016 koluku
# https://github.com/koluku/sudden-death/blob/master/LICENSE


def text_length_list(text: list) -> list:
    """
    各行で何文字あるかリストで返す
    """

    count_list = list()

    for line in text:
        count = 0

        for character in line:
            if unicodedata.east_asian_width(character) in 'FWA':
                # 全角は2文字として数える
                count += 2
            else:
                # 半角なら1文字として数える
                count += 1

        count_list.append(count)

    return count_list


def generator(msg: str) -> str:
    """
    ＿人人人人人人＿
    ＞  突然の死  ＜
    ￣^Y^Y^Y^Y^Y^Y￣
    を作る
    """
    msg_list = msg.split('\n')
    msg_length_list = text_length_list(msg_list)
    max_line_length = max(msg_length_list)
    half_max_line_length = max_line_length // 2
    generating = '＿'

    for _ in range(half_max_line_length + 2):
        generating += '人'

    generating += '＿\n'

    for line_length, message in zip(msg_length_list, msg):
        half_length = (max_line_length - line_length) // 2
        generating += '＞'

        for _ in range(half_length + 2):
            generating += ' '

        generating += message

        for _ in range(max_line_length - half_length - line_length + 2):
            generating += ' '

        generating += '＜\n'

    generating += '￣'

    for _ in range(half_max_line_length + 2):
        generating += '^Y'

    generating += '￣'
    return generating
