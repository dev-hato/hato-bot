# coding: utf-8

"""
おみくじを返す
"""

from dataclasses import dataclass
from random import choices
from typing import Tuple, TypeVar


@dataclass
class OmikujiResult:
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
        assert self.message != ""


TOmikujiEnum = TypeVar("TOmikujiEnum")
OmikujiResults = dict[TOmikujiEnum, OmikujiResult]


def draw(entries: OmikujiResults) -> Tuple[TOmikujiEnum, OmikujiResult]:
    """
    おみくじを引く
    """

    return choices(
        population=list(entries.items()),
        weights=list(map(lambda entry: entry.appearance, entries.values())),
        k=1,
    )[0]
