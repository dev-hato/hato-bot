"""
パワーワード機能
"""

import psycopg

from library.database import Database


class VocabularyDatabase(Database):
    """パワーワードを扱うDBを操作するためのクラス"""

    def get_word_list(self):
        """パワーワードの一覧をDBから取得する"""
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("SELECT no, word FROM vocabulary ORDER BY no;")
                results = cursor.fetchall()
            except psycopg.Error:
                print("Can not execute sql(select_list).")

        return results

    def get_random_word(self):
        """パワーワードをDBからランダムで取得する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("SELECT word FROM vocabulary ORDER BY random() LIMIT 1;")
                results = cursor.fetchone()
            except psycopg.Error:
                print("Can not execute sql(select_random).")

        return results

    def add_word(self, word: str) -> None:
        """パワーワードをDBに登録する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO vocabulary(word) VALUES(%s);", (word,))
                self.conn.commit()
            except psycopg.Error:
                print("Can not execute sql(add).")

    def delete_word(self, word_id: int) -> None:
        """指定したidのパワーワードをDBから削除する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM vocabulary WHERE no = %s;", (word_id,))
                self.conn.commit()
            except psycopg.Error:
                print("Can not execute sql(delete).")


def get_vocabularys():
    """一覧を表示する"""

    with VocabularyDatabase() as v_d:
        result = v_d.get_word_list()

    if len(result) > 0:
        slack_msg = "```"

        # SELECTした順に連番を振る。
        cnt = 1
        for row in result:
            _, text = row
            slack_msg = slack_msg + f"\n {cnt}. {text}"
            cnt += 1

        slack_msg = slack_msg + "\n```"

        return slack_msg
    return "登録されている単語はないっぽ！"


def add_vocabulary(msg: str) -> None:
    """追加する"""

    with VocabularyDatabase() as v_d:
        v_d.add_word(msg)


def show_vocabulary(word_id: int) -> str:
    """指定したものを表示する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    with VocabularyDatabase() as v_d:
        result = v_d.get_word_list()

    cnt = 1
    for row in result:
        _, text = row
        if cnt == word_id:
            slack_msg = text
        cnt += 1

    return slack_msg


def show_random_vocabulary() -> str:
    """ランダムに一つ表示する"""

    slack_msg = "鳩は唐揚げ！！"

    with VocabularyDatabase() as v_d:
        result = v_d.get_random_word()

    if result is not None and len(result) > 0:
        slack_msg = result[0]

    return slack_msg


def delete_vocabulary(word_id: int) -> str:
    """削除する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    with VocabularyDatabase() as v_d:
        result = v_d.get_word_list()
        cnt = 1
        for row in result:
            row_id, _ = row
            if cnt == word_id:
                delete_id = row_id
                v_d.delete_word(delete_id)
                slack_msg = "忘れたっぽ!"
                break
            cnt += 1

    return slack_msg
