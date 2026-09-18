"""
DBを操作するためのベースクラス
"""

import psycopg

import slackbot_settings as conf


def execute_sql(sql: str) -> None:
    """SQLを実行する"""

    with psycopg.connect(conf.DB_URL) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"Execute: {sql}")
            except Exception as _e:
                print("Can not execute sql(create_table).")
                raise _e
