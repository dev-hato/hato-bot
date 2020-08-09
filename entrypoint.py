# coding: utf-8

"""
Dockerのエントリーポイント
"""

import create_env
import run
import wait_db


def main():
    wait_db.main()
    create_env.main()
    run.main()


if __name__ == "__main__":
    main()
