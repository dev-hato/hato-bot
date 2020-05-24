import re
import unittest
from unittest.mock import MagicMock

from slackbot.manager import PluginsManager

from plugins.hato import split_command, respond_to_with_space


class TestRespondToWithSpace(unittest.TestCase):
    def test_normal(self):
        func = MagicMock()
        func.__name__ = 'test'
        wrapper = respond_to_with_space('^amesh kyoko$')
        wrapper(func)
        self.assertEqual(PluginsManager.commands['respond_to'][re.compile('^\s*amesh[ 　]kyoko$', 0)], func)


class TestSplitCommand(unittest.TestCase):
    def test_only_hankaku_space(self):
        self.assertEqual(split_command(' 天気 東京'), ['天気', '東京'])

    def test_only_zenkaku_space(self):
        self.assertEqual(split_command('　天気　東京'), ['天気', '東京'])

    def test_hankaku_and_zenkaku_space(self):
        self.assertEqual(split_command(' 天気　東京'), ['天気', '東京'])

    def test_zenkaku_and_hankaku_space(self):
        self.assertEqual(split_command('　天気 東京'), ['天気', '東京'])

    def test_last_hankaku_space(self):
        self.assertEqual(split_command(' 天気 東京 '), ['天気', '東京'])

    def test_last_zenkaku_space(self):
        self.assertEqual(split_command(' 天気 東京　'), ['天気', '東京'])

    def test_maxsplit(self):
        self.assertEqual(split_command(' text add テスト', 1),
                         ['text', 'add テスト'])


if __name__ == '__main__':
    unittest.main()
