"""
鳩は唐揚げのテスト
"""

import unittest

from library.hatokaraage import hato_ha_karaage


class TestHatoHaKaraage(unittest.TestCase):
    """
    鳩を確実に唐揚げにするテスト
    """

    def test_normal(self):
        """
        鳩じゃないものは唐揚げにはならない
        """
        self.assertEqual(hato_ha_karaage("hoge"), "hoge")

    def test_include_hato(self):
        """
        鳩であれば唐揚げになる
        """
        self.assertEqual(hato_ha_karaage("鳩は唐揚げではない"), "鳩は唐揚げ")


if __name__ == "__main__":
    unittest.main()
