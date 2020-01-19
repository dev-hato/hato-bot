import pg8000
import slackbot_settings as conf

class VocabularyDatabase:
    def __init__(self):
        try: 
            pg8000.paramstyle = 'qmark'
            self.conn = pg8000.connect(
                host=conf.DB_HOST,
                user=conf.DB_USER,
                password=conf.DB_PASSWORD,
                port=conf.DB_PORT,
                ssl=conf.DB_SSL,
                database=conf.DB_NAME
            )
        except:
            print('Can not connect to database.')

    def get_word_list(self):
        cursor = self.conn.cursor()
        try: 
            cursor.execute("SELECT no, word FROM vocabulary ORDER BY no;")
            results = cursor.fetchall()
        except:
            print('Can not execute sql(select_list).')
        cursor.close()
        return results

    def add_word(self, word) -> str:
        cursor = self.conn.cursor()
        try: 
            cursor.execute("INSERT INTO vocabulary(word) VALUES(?);", (word,))
            self.conn.commit()
        except:
            print('Can not execute sql(add).')
        cursor.close()

    def delete_word(self, id) -> int:
        cursor = self.conn.cursor()
        try: 
            cursor.execute("DELETE FROM vocabulary WHERE no = ?;", (id,))
            self.conn.commit()
        except:
            print('Can not execute sql(delete).')
        cursor.close()

    def close(self):
        self.conn.close()

# 一覧を表示する
def get_vocabularys():
    z = VocabularyDatabase()
    result = z.get_word_list()
    slack_msg ="```"

    # SELECTした順に連番を振る。
    cnt = 1

    for row in result:
        no, text = row
        slack_msg = slack_msg + '\n {0}. {1}'.format(cnt, text)
        cnt += 1

    slack_msg = slack_msg +"```"
    z.close()
    return slack_msg

# 追加する
def add_vocabulary(msg) -> str:
    z = VocabularyDatabase()
    result = z.add_word(msg)
    z.close()

# 指定したものを表示する
def show_vocabulary(id) -> int:
    z = VocabularyDatabase()
    result = z.get_word_list()
    slack_msg = "該当する番号は見つからなかったっぽ!"

    cnt = 1

    for row in result:
        no, text = row
        if cnt == id:
            slack_msg = '{}'.format(text)
        cnt += 1
    z.close()
    return slack_msg

# 削除する
def delete_vocabulary(id) -> int:
    z = VocabularyDatabase()
    result = z.get_word_list()
    slack_msg = "該当する番号は見つからなかったっぽ!"

    cnt = 1

    for row in result:
        no, text = row
        if cnt == id:
            delete_id = no
            z.delete_word(delete_id)
            slack_msg = "忘れたっぽ!"
            break
        cnt += 1
    z.close()
    return slack_msg