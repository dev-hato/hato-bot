# coding: utf-8

"""
吹き出し用にtextを装飾する
"""

from sudden_death import generator as sd_generator


def generator(msg: str) -> str:
    """
    ＿人人人人人人＿
    ＞  突然の死  ＜
    ￣^Y^Y^Y^Y^Y^Y￣
    を作る
    """
    return sd_generator(msg)
