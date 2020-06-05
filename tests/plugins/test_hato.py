import re
import unittest
from unittest.mock import MagicMock

from slackbot.manager import PluginsManager

from plugins.hato import split_command, respond_to_with_space


class TestRespondToWithSpace(unittest.TestCase):
    @staticmethod
    def func():
        func = MagicMock()
        func.__name__ = 'test'
        return func

    def test_normal(self):
        func = self.func()
        respond_to_with_space(r'^amesh kyoko$')(func)
        pattern = re.compile(r'^\s*amesh\s*kyoko$')
        self.assertEqual(PluginsManager.commands['respond_to'][pattern], func)

    def test_flag(self):
        func = self.func()
        flag = re.DOTALL
        respond_to_with_space(r'^amesh kyoko$', flag)(func)
        pattern = re.compile(r'^\s*amesh\s*kyoko$', flag)
        self.assertEqual(PluginsManager.commands['respond_to'][pattern], func)


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
