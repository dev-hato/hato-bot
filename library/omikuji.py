# coding: utf-8

"""
おみくじを返す
"""

from typing import Hashable
from enum import Enum, auto
from dataclasses import dataclass
from functools import reduce
from random import choices


@dataclass
class OmikujiResult():
    """
    おみくじの引いた結果を示すデータクラス
    出やすさの調整もここで行う
    """
    appearance: int
    message: str

    def __post_init__(self):
        """
        初期化後のアサーション
        """
        assert self.appearance > 0
        assert self.message != ''


class Omikuji:
    """
    おみくじのコアロジック
    ガチャではないので排出率を公開するメソッドはあえて実装されていない
    """

    def __init__(self, entries: dict[Hashable, OmikujiResult]):
        self.entries = entries

    def draw(self) -> (Hashable, OmikujiResult):
        """
        おみくじを引く
        """
        return choices(
            population=list(self.entries.items()),
            weights=list(map(lambda entry: entry.appearance, self.entries.values())),
            k=1
        )[0]


# 以下おみくじの設定

omikuji = Omikuji(entries={
    'DAI_KICHI': OmikujiResult(
        200,
        ":tada: 大吉 何でもうまくいく!!気がする!!"
    ),
    'CHU_KICHI': OmikujiResult(
        2000,
        ":smile: 中吉 そこそこうまくいくかも!?"
    ),
    'SHO_KICHI': OmikujiResult(
        3800,
        ":smily: 小吉 なんとなくうまくいくかも!?"
    ),

    'KICHI': OmikujiResult(
        3000,
        ":smirk: 吉 まあうまくいくかも!?"
    ),
    'HATO_KICHI': OmikujiResult(
        900,
        ":dove_of_peace: 鳩吉 お前がになる番だ!!羽ばたけ!!!飛べ!!!!唐揚げになれ!!!!!"
    ),

   'KYO': OmikujiResult(
        75,
        ":cry: 凶 ちょっと慎重にいったほうがいいかも……"
    ),

    'DAI_KYO': OmikujiResult(
        25,
        ":crying_cat_face: 大凶 そういう時もあります……猫になって耐えましょう"
    ),

})


def draw() -> str:
    """
    おみくじ抽選
    """
    return omikuji.draw()[1].message
