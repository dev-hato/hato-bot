"""
初回動かす必要のあるスクリプト
"""

import pg8000
import slackbot_settings as conf


class CreateEnvDatabase:
    """
    DBのテーブル作成用スクリプト
    初回環境構築時のみ必要
    """

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
        except:
            print('Can not connect to database.')
            raise

    def __enter__(self):
        return self

    def execute_sql(self, sql: str) -> None:
        """SQLを実行する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                self.conn.commit()
                print('Create table. {}'.format(sql))
            except Exception as _e:
                print('Can not execute sql(create_table).')
                raise _e

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def create_table() -> None:
    """テーブルを作成する"""

    with CreateEnvDatabase() as _db, open('setup/pgsql-init/02_init.sql') as init_sql:
        for line in init_sql.readlines():
            _db.execute_sql(line)


def main():
    """メイン関数"""

    create_table()


if __name__ == "__main__":
    main()
