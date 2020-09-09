"""
初回動かす必要のあるスクリプト
"""

from library.database import Database


def create_table() -> None:
    """テーブルを作成する"""

    with Database() as _db, open("setup/pgsql-init/02_init.sql") as init_sql:
        for line in init_sql.readlines():
            _db.execute_sql(line)


def main():
    """メイン関数"""

    create_table()


if __name__ == "__main__":
    main()
