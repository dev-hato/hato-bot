"""
hato.pyのテスト
"""

import re
import unittest
from unittest.mock import MagicMock

from slackbot.manager import PluginsManager

from plugins.hato import split_command, respond_to_with_space


class TestRespondToWithSpace(unittest.TestCase):
    """
    スペースが含まれているときのテスト
    """
    @staticmethod
    def func() -> MagicMock:
        """ mockを返す """
        func = MagicMock()
        func.__name__ = 'test'
        return func

    def test_normal(self):
        """ 通常パターン """
        func = self.func()
        respond_to_with_space(r'^amesh kyoko$')(func)
        pattern = re.compile(r'^\s*amesh\s*kyoko$')
        self.assertEqual(PluginsManager.commands['respond_to'][pattern], func)

    def test_flag(self):
        """ 改行が含まれる場合のマッチフラグが入ったパターン """
        func = self.func()
        flag = re.DOTALL
        respond_to_with_space(r'^amesh kyoko$', flag)(func)
        pattern = re.compile(r'^\s*amesh\s*kyoko$', flag)
        self.assertEqual(PluginsManager.commands['respond_to'][pattern], func)


class TestSplitCommand(unittest.TestCase):
    """
    split commandのテスト
    """

    def test_only_hankaku_space(self):
        """ 半角スペースのみのテストケース """
        self.assertEqual(split_command(' 天気 東京'), ['天気', '東京'])

    def test_only_zenkaku_space(self):
        """ 全角スペースのみのテストケース """
        self.assertEqual(split_command('　天気　東京'), ['天気', '東京'])

    def test_hankaku_and_zenkaku_space(self):
        """ 半角スペースと全角スペースが混ざったテストケース1 """
        self.assertEqual(split_command(' 天気　東京'), ['天気', '東京'])

    def test_zenkaku_and_hankaku_space(self):
        """ 半角スペースと全角スペースが混ざったテストケース2 """
        self.assertEqual(split_command('　天気 東京'), ['天気', '東京'])

    def test_last_hankaku_space(self):
        """ 行末に半角スペースが入ったテストケース """
        self.assertEqual(split_command(' 天気 東京 '), ['天気', '東京'])

    def test_last_zenkaku_space(self):
        """ 行末に全角スペースが入ったテストケース """
        self.assertEqual(split_command(' 天気 東京　'), ['天気', '東京'])

    def test_maxsplit(self):
        """ 空白が間に2つ以上ある場合 """
        self.assertEqual(split_command(' text add テスト', 1),
                         ['text', 'add テスト'])


if __name__ == '__main__':
    unittest.main()
