# coding: utf-8

"""
おみくじを返す
"""

from enum import Enum, auto
from typing import Tuple, TypeVar, Generic
from dataclasses import dataclass
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

TOmikujiEnum = TypeVar('TOmikujiEnum')

class OmikujiResults(dict[TOmikujiEnum, OmikujiResult]):
    """
    おみくじ結果と出やすさを管理する辞書
    """

    def __init__(self, *args, **kwargs):
        super(OmikujiResults, self).__init__(*args, **kwargs)


def draw(entries: OmikujiResults) -> Tuple[TOmikujiEnum, OmikujiResult]:
    """
    おみくじを引く
    """

    return choices(
        population=list(entries.items()),
        weights=list(
            map(lambda entry: entry.appearance, entries.values())),
        k=1
    )[0]


