"""
DBを操作するためのベースクラス
"""

import psycopg2

import slackbot_settings as conf


class Database:
    """DBを操作するためのベースクラス"""

    def __init__(self):
        try:
            self.conn = psycopg2.connect(conf.DB_URL, sslmode='require')
        except psycopg2.Error:
            print('Can not connect to database.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def execute_sql(self, sql: str) -> None:
        """SQLを実行する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                self.conn.commit()
                print('Execute: {}'.format(sql))
            except Exception as _e:
                print('Can not execute sql(create_table).')
                raise _e
