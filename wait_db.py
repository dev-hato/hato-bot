"""
DBが起動するまで待機する
"""

from time import sleep

import psycopg

from library.database import Database


def wait_db() -> None:
    """DBが起動するまで待機する"""

    max_attempt = 30

    for i in range(max_attempt):
        try:
            with Database() as _db:
                _db.execute_sql("SELECT 1")
                break
        except psycopg.OperationalError as _e:
            if i == max_attempt - 1:
                raise _e

            sleep(1)

    print("postgres is running!")


def main():
    """メイン関数"""

    wait_db()


if __name__ == "__main__":
    main()
