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
        print(self)
        return self

    def execute_sql(self, SQL) -> str:
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(SQL)
                self.conn.commit()
                print('Create table. {}'.format(SQL))
            except:
                print('Can not execute sql(create_table).')

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def create_table():
    with CreateEnvDatabase() as db:
        db.execute_sql(
            "CREATE TABLE IF NOT EXISTS vocabulary(no serial UNIQUE, word text);")
        db.execute_sql(
            "CREATE TABLE IF NOT EXISTS labotter(user_name text UNIQUE, lab_in_flag int, lab_in timestamp, lab_rida timestamp, min_sum int);")


def main():
    create_table()


if __name__ == "__main__":
    main()
