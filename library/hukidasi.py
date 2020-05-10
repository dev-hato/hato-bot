# coding: utf-8
import unicodedata
# Sudden Death(元にしたコードのライセンスは以下の通り)
# MIT License
# Copyright (c) 2016 koluku
# https://github.com/koluku/sudden-death/blob/master/LICENSE

# 突然の死で使う関数


def text_length_list(text):
    count_list = list()

    for t in text:
        count = 0

        for c in t:
            count += 2 if unicodedata.east_asian_width(c) in 'FWA' else 1

        count_list.append(count)

    return count_list


def generator(msg):
    msg = msg.split('\n')
    msg_length_list = text_length_list(msg)
    max_length = max(msg_length_list)
    half_max_length = max_length // 2
    generating = '＿'

    for _ in range(half_max_length + 2):
        generating += '人'

    generating += '＿\n'

    for l, m in zip(msg_length_list, msg):
        half_length = (max_length - l) // 2
        generating += '＞'

        for _ in range(half_length + 2):
            generating += ' '

        generating += m

        for _ in range(max_length - half_length - l + 2):
            generating += ' '

        generating += '＜\n'

    generating += '￣'

    for _ in range(half_max_length + 2):
        generating += '^Y'

    generating += '￣'
    return generating
