"""
DBが起動するまで待機する
"""
from time import sleep

import psycopg2

from library.database import Database


def wait_db() -> None:
    """DBが起動するまで待機する"""

    while True:
        try:
            with Database() as db:
                db.execute_sql('SELECT 1')
                break
        except psycopg2.OperationalError:
            sleep(1)
            pass

    print('postgres is running!')


def main():
    """メイン関数"""

    wait_db()


if __name__ == "__main__":
    main()
