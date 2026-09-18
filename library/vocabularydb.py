"""
パワーワード機能
"""

import psycopg

import slackbot_settings as conf


def get_word_list():
    """パワーワードの一覧をDBから取得する"""
    with psycopg.connect(conf.DB_URL) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT no, word FROM vocabulary ORDER BY no;")
                results = cursor.fetchall()
            except psycopg.Error:
                print("Can not execute sql(select_list).")

    return results


def get_random_word():
    """パワーワードをDBからランダムで取得する"""

    with psycopg.connect(conf.DB_URL) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT word FROM vocabulary ORDER BY random() LIMIT 1;")
                results = cursor.fetchone()
            except psycopg.Error:
                print("Can not execute sql(select_random).")

    return results


def add_word(word: str) -> None:
    """パワーワードをDBに登録する"""

    with psycopg.connect(conf.DB_URL) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO vocabulary(word) VALUES(%s);", (word,))
                conn.commit()
            except psycopg.Error:
                print("Can not execute sql(add).")


def delete_word(word_id: int) -> None:
    """指定したidのパワーワードをDBから削除する"""

    with psycopg.connect(conf.DB_URL) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM vocabulary WHERE no = %s;", (word_id,))
                conn.commit()
            except psycopg.Error:
                print("Can not execute sql(delete).")


def get_vocabularys():
    """一覧を表示する"""

    result = get_word_list()

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

    add_word(msg)


def show_vocabulary(word_id: int) -> str:
    """指定したものを表示する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    result = get_word_list()

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

    result = get_random_word()

    if result is not None and len(result) > 0:
        slack_msg = result[0]

    return slack_msg


def delete_vocabulary(word_id: int) -> str:
    """削除する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    result = get_word_list()
    cnt = 1
    for row in result:
        row_id, _ = row
        if cnt == word_id:
            delete_id = row_id
            delete_word(delete_id)
            slack_msg = "忘れたっぽ!"
            break
        cnt += 1

    return slack_msg
