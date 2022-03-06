"""
omikujiライブラリのテスト
"""

import unittest
from enum import Enum, auto

from library.omikuji import OmikujiResult, Omikuji, test


class TestOmikuji(unittest.TestCase):
    """
    おみくじのテスト
    """

    def test_omikuji_config():
        """
        おみくじの設定が正常か
        """
        test()

    def test_omikuji_minimum(self):
        """
        おみくじの実装が正常か
        """

        class DummyOmikujiResults(Enum):
            """
            テスト用のおみくじ結果Enum
            """
            KICHI = auto()
            SUE_KICHI = auto()

        testOmikuji = Omikuji[DummyOmikujiResults](entries={
            DummyOmikujiResults.KICHI: OmikujiResult(DummyOmikujiResults.KICHI, 0.5, "吉"),
            DummyOmikujiResults.SUE_KICHI: OmikujiResult(DummyOmikujiResults.SUE_KICHI, 0.5, "末吉"),
        })

        self.assertIn(testOmikuji.draw().key, DummyOmikujiResults)
