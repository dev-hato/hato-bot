"""
初回動かす必要のあるスクリプト
"""

from library.database import Database


class CreateEnvDatabase(Database):
    """
    DBのテーブル作成用スクリプト
    初回環境構築時のみ必要
    """

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
