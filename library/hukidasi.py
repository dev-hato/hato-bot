# coding: utf-8

"""
吹き出し用にtextを装飾する
"""

# Sudden Death(元にしたコードのライセンスは以下の通り)
# MIT License
# Copyright (c) 2016 koluku
# https://github.com/koluku/sudden-death/blob/master/LICENSE
from .sudden_death.sd import generator as sd_generator


def generator(msg: str) -> str:
    """
    ＿人人人人人人＿
    ＞  突然の死  ＜
    ￣^Y^Y^Y^Y^Y^Y￣
    を作る
    """
    return sd_generator(msg)
