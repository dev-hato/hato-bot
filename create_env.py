"""
初回動かす必要のあるスクリプト
"""

from library.database import execute_sql


def create_table() -> None:
    """テーブルを作成する"""

    with open(
        "postgres/docker-entrypoint-initdb.d/02_init.sql", encoding="UTF-8"
    ) as init_sql:
        sql = ""
        for line in init_sql.readlines():
            sql += line
            if ";" in line:
                execute_sql(sql)
                sql = ""


def main():
    """メイン関数"""

    create_table()


if __name__ == "__main__":
    main()
