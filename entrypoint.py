# coding: utf-8

"""
Dockerのエントリーポイント
"""

import create_env
import run


def main():
    """メイン関数"""

    create_env.main()
    run.main()


if __name__ == "__main__":
    main()
