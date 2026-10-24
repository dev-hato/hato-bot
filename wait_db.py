"""
DBが起動するまで待機する
"""

from time import sleep

import psycopg

from library.database import execute_sql


def wait_db() -> None:
    """DBが起動するまで待機する"""

    max_attempt = 30

    for i in range(max_attempt):
        try:
            execute_sql("SELECT 1")
            break
        except psycopg.OperationalError:
            if i == max_attempt - 1:
                raise

            sleep(1)

    print("postgres is running!")


def main():
    """メイン関数"""

    wait_db()


if __name__ == "__main__":
    main()
