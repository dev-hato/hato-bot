"""
hato_mikuji.pyのテスト
"""

import unittest
from plugins.hato_mikuji import HatoMikuji


class TestHatoMikuji(unittest.TestCase):
    """
    HatoMikujiの設定テスト
    """

    def test_config_normalized_per_mill(self):
        sum_of_appearance = sum(map(lambda e: e.appearance, HatoMikuji.OMIKUJI_CONFIG.values()))
        self.assertEqual(
            sum_of_appearance,
            1000
        )
        
