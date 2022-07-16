"""
omikujiライブラリのテスト
"""

import unittest
from enum import Enum, auto

from library.omikuji import OmikujiResult, OmikujiResults, draw


class TestOmikuji(unittest.TestCase):
    """
    おみくじのテスト
    """

    def test_omikuji_minimum(self):
        """
        おみくじの実装が正常か
        """

        class DummyOmikujiEnum(Enum):
            """
            おみくじ設定(ダミー)
            """

            KICHI = auto()
            SUE_KICHI = auto()

        dummy_omikuji_results = OmikujiResults(
            {
                DummyOmikujiEnum.KICHI: OmikujiResult(1, "吉"),
                DummyOmikujiEnum.SUE_KICHI: OmikujiResult(1, "末吉"),
            }
        )

        self.assertIn(draw(dummy_omikuji_results)[0], dummy_omikuji_results.keys())
