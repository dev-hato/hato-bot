# coding: utf-8

"""
BotのMain関数
"""
import sys
import logging
import logging.config
from slackbot.bot import Bot


def main():
    """
    Botを起動します
    """
    log_format_config = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout,
    }
    logging.basicConfig(**log_format_config)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
