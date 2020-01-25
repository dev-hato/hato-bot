import pg8000
import slackbot_settings as conf

# DBのテーブル作成用スクリプト
# 初回環境構築時のみ必要

class CreateEnvDatabase:
    def __init__(self):
        try: 
            pg8000.paramstyle = 'qmark'
            self.conn = pg8000.connect(
                host=conf.DB_HOST,
                user=conf.DB_USER,
                password=conf.DB_PASSWORD,
                port=conf.DB_PORT,
                ssl=False,
                database=conf.DB_NAME
            )
        except:
            print('Can not connect to database.')

    def execute_sql(self, SQL) -> str:
        cursor = self.conn.cursor()
        try: 
            cursor.execute(SQL)
            self.conn.commit()
            print('Create table. {}'.format(SQL))
        except:
            print('Can not execute sql(create_table).')
        cursor.close()

    def close(self):
        self.conn.close()

def create_table():
    db = CreateEnvDatabase()
    db.execute_sql("CREATE TABLE IF NOT EXISTS vocabulary(no serial UNIQUE, word text);")
    db.execute_sql("CREATE TABLE IF NOT EXISTS labotter(user_name text UNIQUE, lab_in_flag int, lab_in timestamp, lab_rida timestamp, min_sum int);")
    db.close()
    
def main():
    create_table()

if __name__ == "__main__":
    main()
