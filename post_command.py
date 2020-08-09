# coding: utf-8

"""
localからコマンドを実行するためのスクリプト
"""
import argparse

import requests


def main():
    """メイン関数"""

    parser = argparse.ArgumentParser()
    parser.add_argument('message', type=str)
    args = parser.parse_args()
    requests.post('http://localhost:3000/',
                  json={'message': args.message, 'channel': 'C0123A4B5C6', 'user': 'U012A34BCDE'})


if __name__ == "__main__":
    main()
