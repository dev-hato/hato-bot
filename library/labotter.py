"""
らぼったー機能
"""

import datetime
from typing import Tuple
import psycopg2

from library.database import Database


class LabotterDatabase(Database):
    """
    らぼったーのDB処理
    """

    def check_exist_user_name(self, user_name: str) -> bool:
        """
        ユーザーが存在するかどうか確認する
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM labotter WHERE user_name = %s;", (user_name,))
            row = int(cursor.fetchone()[0])
            return row != 0

    def check_lab_in_flag(self, user_name: str) -> bool:
        """
        らぼいんしているかどうか
        """
        lab_in_flag = False
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT lab_in_flag FROM labotter WHERE user_name = %s;", (user_name,))
            lab_in_flag = cursor.fetchone()[0]

        return bool(lab_in_flag)

    def create_labo_row(self, user_name: str) -> bool:
        """
        らぼったー会員登録
        """
        c_lab_row_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO
                    labotter(user_name, lab_in_flag, lab_in, lab_rida, min_sum)
                    VALUES (%s, '0', null, null, '0');
                    """, (user_name,))
                self.conn.commit()
            except psycopg2.Error:
                c_lab_row_flag = False
                print('Can not execute sql(add).')

        return c_lab_row_flag

    def registory_labo_in(self, user_name: str, start_time: str) -> bool:
        """
        らぼいん
        """
        r_lab_in_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("UPDATE labotter SET \
                lab_in_flag = '1', \
                lab_in = %s \
                WHERE user_name = %s;", (start_time, user_name,))
                self.conn.commit()
            except psycopg2.Error:
                r_lab_in_flag = False
                print('Can not execute sql(labo_in).')

        return r_lab_in_flag

    def registory_labo_rida(self, user_name: str, end_time: str, add_sum: int) -> bool:
        """
        らぼりだ
        """
        r_lab_rida_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("UPDATE labotter SET \
                lab_in_flag = '0', \
                min_sum = %s, \
                lab_rida = %s \
                WHERE user_name = %s;", (add_sum, end_time, user_name,))
                self.conn.commit()
            except psycopg2.Error:
                r_lab_rida_flag = False
                print('Can not execute sql(labo_rida).')

        return r_lab_rida_flag

    def get_labo_in_time_and_sum_time(self, user_name: str) -> Tuple[str, int]:
        """
        らぼいん時間とらぼ滞在時間合計を返す
        """
        labo_in_time = None
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT lab_in, min_sum FROM labotter WHERE user_name = %s;", (user_name,))
            labo_in_time, min_sum = cursor.fetchone()
        return labo_in_time, min_sum


def labo_in(user_name: str) -> Tuple[bool, str]:
    """らぼいん処理"""

    success_flag = False  # 登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    start_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    with LabotterDatabase() as lab:
        # 初回登録時の処理
        if not lab.check_exist_user_name(user_name):
            lab.create_labo_row(user_name)
        # らぼりだ中ならば処理をする
        if not lab.check_lab_in_flag(user_name):
            success_flag = lab.registory_labo_in(user_name, start_time)

    return success_flag, start_time


def labo_rida(user_name: str) -> Tuple[bool, str, int, int]:
    """らぼりだ処理"""

    success_flag = False  # 登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    diff_time = 0
    min_sum = 0
    end_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    with LabotterDatabase() as lab:
        # 初回登録時の処理
        if not lab.check_exist_user_name(user_name):
            lab.create_labo_row(user_name)

        # らぼいん中ならば処理をする
        if lab.check_lab_in_flag(user_name):
            labo_in_time, min_sum = lab.get_labo_in_time_and_sum_time(
                user_name)
            start_time = datetime.datetime.strptime(
                str(labo_in_time), '%Y-%m-%d %H:%M:%S')
            diff_time = int((dt_now - start_time).total_seconds())
            min_sum = min_sum + diff_time
            success_flag = lab.registory_labo_rida(
                user_name, end_time, min_sum)

    return success_flag, end_time, diff_time, min_sum
