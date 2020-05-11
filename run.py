# coding: utf-8
import sys
import logging
import logging.config
from slackbot import settings
from slackbot.bot import Bot


def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
