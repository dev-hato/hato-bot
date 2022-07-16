"""
初回動かす必要のあるスクリプト
"""

from library.database import Database


def create_table() -> None:
    """テーブルを作成する"""

    with Database() as _db, open(
        "postgres/docker-entrypoint-initdb.d/02_init.sql", encoding="UTF-8"
    ) as init_sql:
        sql = ""
        for line in init_sql.readlines():
            sql += line
            if ";" in line:
                _db.execute_sql(sql)
                sql = ""


def main():
    """メイン関数"""

    create_table()


if __name__ == "__main__":
    main()
