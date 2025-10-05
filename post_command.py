# coding: utf-8

"""
localからコマンドを実行するためのスクリプト
"""
import argparse

import requests


def main():
    """メイン関数"""

    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str, help="投稿するメッセージ")
    parser.add_argument("--channel", type=str, help="投稿先のチャンネルのchannel id")
    parser.add_argument("--user", type=str, help="メッセージを送ったユーザーのuser id")
    args = parser.parse_args()
    requests.post(
        "http://localhost:3000/",
        json={"message": args.message, "channel": args.channel, "user": args.user},
    )


if __name__ == "__main__":
    main()
