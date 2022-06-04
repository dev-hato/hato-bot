"""
hukidashiライブラリのテスト
"""

import textwrap
import unittest

from library.hukidasi import generator


class TestHukidashiGenerator(unittest.TestCase):
    """
    突然の死を生成するテスト
    """

    def test_normal_one_line_ascii(self):
        """
        英数字のみの1行のテキストに対して突然の死が生成される
        """
        self.assertEqual(
            generator("Hello, pegion!"),
            textwrap.dedent(
                """\
        ＿人人人人人人人人人＿
        ＞  Hello, pegion!  ＜
        ￣^Y^Y^Y^Y^Y^Y^Y^Y^Y￣"""
            ),
        )

    def test_normal_one_line_zenkaku(self):
        """
        全角を含む1行のテキストに対して突然の死が生成される
        """
        self.assertEqual(
            generator("言うことを聞け"),
            textwrap.dedent(
                """\
        ＿人人人人人人人人人＿
        ＞  言うことを聞け  ＜
        ￣^Y^Y^Y^Y^Y^Y^Y^Y^Y￣"""
            ),
        )

    def test_normal_multiline(self):
        """
        複数行のテキストに対して突然の死が生成される
        """
        self.assertEqual(
            generator("そして、\n鳩は唐揚げになる"),
            textwrap.dedent(
                """\
        ＿人人人人人人人人人人＿
        ＞      そして、      ＜
        ＞  鳩は唐揚げになる  ＜
        ￣^Y^Y^Y^Y^Y^Y^Y^Y^Y^Y￣"""
            ),
        )
