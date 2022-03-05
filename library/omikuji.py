# coding: utf-8

"""
おみくじを返す
"""

from abc import ABC
from enum import Enum
from dataclasses import dataclass
from functools import reduce
from random import choices


class AbstractOmikujiResults(ABC)


"""
    おみくじの結果一覧の抽象クラス
    """
pass


"""
Enumを継承している
"""

AbstractOmikujiResults.register(Enum)


@dataclass
class OmikujiResult:
    key: AbstractOmikujiResults
    rate: float
    message: str

    def test(self):
        assert isinstance(key, AbstractOmikujiResults)
        assert rate < 1
        assert message != ''


class Omikuji:
    """
    おみくじのコアロジック
    ガチャではないので排出率を公開するメソッドはあえて実装されていない
    """

    def __init__(self, entries: dict[AbstractOmikujiResults, OmikujiResult]):
        self.entries = entries

    def test(self):
        """
        全体のテストを行う

        各エントリーのテスト、 排出率の合計が1であること、エントリーのキーが不整合のテストをする
        """
        for entry in values(self.entries):
            entry.test

        assert reduce(lambda acc, cur: acc + cur.rate, self.entries, 0) == 1.0
        assert len(filter(lambda key, value: key !=
                   value.key, self.entries)) == 0

    def draw(self):
        """
        おみくじを引く
        """
        return choices(
            population=self.entries,
            weights=map(lambda entry: entry.rate, self.entries)
            k=1
        )[0]


"""
以下おみくじの設定
"""


class OmikujiResults(AbstractOmikujiResults):
    DaiKichi = auto()
    ChuKichi = auto()
    ShoKichi = auto()
    HatoKichi = auto()
    Kichi = auto()
    Kyo = auto()
    DaiKyo = auto()


omikuji = Omikuji(entries={
    OmikujiResults.DaiKichi: OmikujiResult(OmikujiResults.DaiKichi, 0.02, ":tada: 大吉 何でもうまくいく!!気がする!!"),
    OmikujiResults.ChuKichi: OmikujiResult(OmikujiResults.ChuKichi, 0.2, ":smile: 中吉 そこそこうまくいくかも!?"),
    OmikujiResults.SyoKichi: OmikujiResult(OmikujiResults.ShoKichi, 0.38, ":smily: 小吉 なんとなくうまくいくかも!?"),
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
