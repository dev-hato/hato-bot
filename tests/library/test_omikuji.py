"""
omikujiライブラリのテスト
"""

import unittest
from library.omikuji import OmikujiResult, Omikuji, test
from enum import Enum, auto


class TestOmikuji(unittest.TestCase):
    """
    おみくじのテスト
    """

    def test_omikuji_config(self):
        """
        おみくじの設定が正常か
        """
        test()

    def test_omikuji_minimum(self):
        """
        おみくじの実装が正常か
        """

        class TestOmikujiResults(Enum):
            Kichi = auto()
            SueKichi = auto()

        testOmikuji = Omikuji[TestOmikujiResults](entries={
            TestOmikujiResults.Kichi: OmikujiResult(TestOmikujiResults.Kichi, 0.5, "吉"),
            TestOmikujiResults.SueKichi: OmikujiResult(TestOmikujiResults.SueKichi, 0.5, "末吉"),
        })

        self.assertIn(testOmikuji.draw().key, TestOmikujiResults)
