"""
DBを操作するためのベースクラス
"""

import pg8000

import slackbot_settings as conf


class Database:
    """DBを操作するためのベースクラス"""

    def __init__(self):
        try:
            pg8000.paramstyle = 'qmark'
            self.conn = pg8000.connect(
                host=conf.DB_HOST,
                user=conf.DB_USER,
                password=conf.DB_PASSWORD,
                port=conf.DB_PORT,
                ssl_context=conf.DB_SSL,
                database=conf.DB_NAME
            )
        except pg8000.Error:
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
