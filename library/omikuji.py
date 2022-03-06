# coding: utf-8

"""
おみくじを返す
"""

from abc import ABC
from enum import Enum, auto
from dataclasses import dataclass
from functools import reduce
from random import choices
from typing import TypeVar, Generic


TOmikujiEnum = TypeVar('TOmikujiEnum')

@dataclass
class OmikujiResult:
    key: TOmikujiEnum
    rate: float
    message: str

    def test(self):
        assert isinstance(self.key, Enum)
        assert self.rate < 1
        assert self.message != ''


class Omikuji(Generic[TOmikujiEnum]):
    """
    おみくじのコアロジック
    ガチャではないので排出率を公開するメソッドはあえて実装されていない
    """

    def __init__(self, entries: dict[TOmikujiEnum, OmikujiResult]):
        self.entries = entries

    def test(self):
        """
        全体のテストを行う

        各エントリーのテスト、 排出率の合計が1であること、エントリーのキーが不整合のテストをする
        """
        for entry in self.entries.values():
            entry.test()

        assert round(reduce(lambda acc, cur: acc + cur.rate, self.entries.values(), 0), 1) == 1
        assert len(list(filter(lambda item: (item[0] != item[1].key), self.entries.items()))) == 0

    def draw(self):
        """
        おみくじを引く
        """
        return choices(
            population=list(self.entries.items()),
            weights=map(lambda entry: entry.rate, self.entries.values()),
            k=1
        )[0][1]


# 以下おみくじの設定

class OmikujiResults(Enum):
    DaiKichi = auto()
    ChuKichi = auto()
    ShoKichi = auto()
    HatoKichi = auto()
    Kichi = auto()
    Kyo = auto()
    DaiKyo = auto()


omikuji = Omikuji[OmikujiResults](entries={
    OmikujiResults.DaiKichi: OmikujiResult(OmikujiResults.DaiKichi, 0.02, ":tada: 大吉 何でもうまくいく!!気がする!!"),
    OmikujiResults.ChuKichi: OmikujiResult(OmikujiResults.ChuKichi, 0.2, ":smile: 中吉 そこそこうまくいくかも!?"),
    OmikujiResults.ShoKichi: OmikujiResult(OmikujiResults.ShoKichi, 0.38, ":smily: 小吉 なんとなくうまくいくかも!?"),
    OmikujiResults.Kichi: OmikujiResult(OmikujiResults.Kichi, 0.3, ":smirk: 吉 まあうまくいくかも!?"),
    OmikujiResults.HatoKichi: OmikujiResult(OmikujiResults.HatoKichi, 0.09, ":dove_of_peace: 鳩吉 お前がになる番だ!!羽ばたけ!!!飛べ!!!!唐揚げになれ!!!!!"),
    OmikujiResults.Kyo: OmikujiResult(OmikujiResults.Kyo, 0.0075, ":cry: 凶 ちょっと慎重にいったほうがいいかも……"),
    OmikujiResults.DaiKyo: OmikujiResult(OmikujiResults.DaiKyo, 0.0025, ":crying_cat_face: 大凶 そういう時もあります……猫になって耐えましょう"),
})


def test():
    """
    おみくじの設定テスト
    """

    omikuji.test()


def draw():
    """
    おみくじ抽選
    """
    return omikuji.draw().message
