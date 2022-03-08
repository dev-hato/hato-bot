"""
omikujiライブラリのテスト
"""

import unittest
from enum import Enum, auto

from library.omikuji import OmikujiResult, Omikuji


class TestOmikuji(unittest.TestCase):
    """
    おみくじのテスト
    """

    def test_omikuji_minimum(self):
        """
        おみくじの実装が正常か
        """
        dummy_omikuji = Omikuji(entries={
            'KICHI': OmikujiResult(1, "吉"),
            'SUE_KICHI': OmikujiResult(1, "末吉"),
        })

        self.assertIn(dummy_omikuji.draw()[0], dummy_omikuji.entries.keys())
