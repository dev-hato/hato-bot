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
                  json={'message': args.message, 'channel': 'C0189D2B8F7', 'user': 'U018B02SXFD'})


if __name__ == "__main__":
    main()
