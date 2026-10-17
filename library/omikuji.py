"""
おみくじを返す
"""

from dataclasses import dataclass
from random import choices
from typing import TypeVar


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


def draw(entries: OmikujiResults) -> tuple[TOmikujiEnum, OmikujiResult]:
    """
    おみくじを引く
    """

    return choices(
        population=list(entries.items()),
        weights=[entry.appearance for entry in entries.values()],
        k=1,
    )[0]
