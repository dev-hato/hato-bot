"""
omikujiライブラリのテスト
"""

import unittest
from library.omikuji import AbstractOmikujiResults, OmikujiResult, Omikuji, test
from Enum import auto


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

        class TestOmikujiResults(AbstractOmikujiResults):
            Kichi = auto()
            SueKichi = auto()

        testOmikuji = Omikuji(entries={
            TestOmikujiResults.Kichi: OmikujiResult(TestOmikujiResults.Kichi, 0.5, "吉"),
            TestOmikujiResults.SueKichi: OmikujiResult(TestOmikujiResults.SueKichi, 0.5, "末吉"),
        })

        self.assertTrue(
            testOmikuji.draw().message == "吉"
            or testOmikuji.draw().message == "末吉"
        )
