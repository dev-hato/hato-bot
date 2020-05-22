import pg8000
import datetime
import slackbot_settings as conf


class LabotterDatabase:
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

    def __enter__(self):
        return self

    def check_exist_id(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM labotter WHERE user_name = ?;", (id,))
            row = int(cursor.fetchone()[0])
            return row

    def check_lab_in_flag(self, id):
        lab_in_flag = False
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT lab_in_flag FROM labotter WHERE user_name = ?;", (id,))
            lab_in_flag = cursor.fetchone()[0]

        return lab_in_flag

    def create_labo_row(self, id):
        c_lab_row_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO labotter(user_name, lab_in_flag, lab_in, lab_rida, min_sum) VALUES (?, '0', null, null, '0');", (id,))
                self.conn.commit()
            except:
                c_lab_row_flag = False
                print('Can not execute sql(add).')

        return c_lab_row_flag

    def registory_labo_in(self, id, start_time):
        r_lab_in_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("UPDATE labotter SET \
                lab_in_flag = '1', \
                lab_in = ? \
                WHERE user_name = ?;", (start_time, id,))
                self.conn.commit()
            except:
                r_lab_in_flag = False
                print('Can not execute sql(labo_in).')

        return r_lab_in_flag

    def registory_labo_rida(self, id, end_time, add_sum):
        r_lab_rida_flag = True
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("UPDATE labotter SET \
                lab_in_flag = '0', \
                min_sum = ?, \
                lab_rida = ? \
                WHERE user_name = ?;", (add_sum, end_time, id,))
                self.conn.commit()
            except:
                r_lab_rida_flag = False
                print('Can not execute sql(labo_rida).')

        return r_lab_rida_flag

    def get_labo_in_time_and_sum_time(self, id):
        labo_in_time = None
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT lab_in, min_sum FROM labotter WHERE user_name = ?;", (id,))
            labo_in_time, min_sum = cursor.fetchone()
        return labo_in_time, min_sum

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def labo_in(user_id) -> str:
    """らぼいん処理"""

    success_flag = False  # 登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    start_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    with LabotterDatabase() as lab:
        # 初回登録時の処理
        if lab.check_exist_id(user_id) == 0:
            lab.create_labo_row(user_id)
        # らぼりだ中ならば処理をする
        if lab.check_lab_in_flag(user_id) == False:
            success_flag = lab.registory_labo_in(user_id, start_time)

    return success_flag, start_time


def labo_rida(user_id) -> str:
    """らぼりだ処理"""

    success_flag = False  # 登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    dt = 0
    diff_time = 0
    min_sum = 0
    end_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    with LabotterDatabase() as lab:
        # 初回登録時の処理
        if lab.check_exist_id(user_id) == 0:
            lab.create_labo_row(user_id)
        # らぼいん中ならば処理をする
        if lab.check_lab_in_flag(user_id) == True:
            labo_in_time, min_sum = lab.get_labo_in_time_and_sum_time(user_id)
            start_time = datetime.datetime.strptime(
                str(labo_in_time), '%Y-%m-%d %H:%M:%S')
            dt = dt_now - start_time
            diff_time = int(dt.total_seconds())
            min_sum = min_sum + diff_time
            success_flag = lab.registory_labo_rida(user_id, end_time, min_sum)

    return success_flag, end_time, diff_time, min_sum
