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

    def check_exist_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM labotter WHERE user_name = ?;", (id,))
        row = int(cursor.fetchone()[0])
        cursor.close()
        return row
    
    def check_lab_in_flag(self, id):
        lab_in_flag = False
        cursor = self.conn.cursor()
        cursor.execute("SELECT lab_in_flag FROM labotter WHERE user_name = ?;", (id,))
        lab_in_flag = cursor.fetchone()[0]
        cursor.close()
        return lab_in_flag

    def create_labo_row(self, id):
        c_lab_row_flag = True
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO labotter(user_name, lab_in_flag, lab_in, lab_rida, min_sum) VALUES (?, '0', null, null, '0');", (id,))
            self.conn.commit()
        except:
            c_lab_row_flag = False
            print('Can not execute sql(add).')
        cursor.close()
        return c_lab_row_flag

    def registory_labo_in(self, id, start_time):
        r_lab_in_flag = True
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE labotter SET \
            lab_in_flag = '1', \
            lab_in = ? \
            WHERE user_name = ?;", (start_time,id,))
            self.conn.commit()
        except:
            r_lab_in_flag = False
            print('Can not execute sql(labo_in).')
        cursor.close()
        return r_lab_in_flag

    def registory_labo_rida(self, id, end_time):
        r_lab_rida_flag = True
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE labotter SET \
            lab_in_flag = '0', \
            lab_rida = ? \
            WHERE user_name = ?;", (end_time,id,))
            self.conn.commit()
        except:
            r_lab_rida_flag = False
            print('Can not execute sql(labo_rida).')
        cursor.close()
        return r_lab_rida_flag

    def get_labo_in_time(self, id):
        labo_in_time = None
        cursor = self.conn.cursor()
        cursor.execute("SELECT lab_in FROM labotter WHERE user_name = ?;", (id,))
        labo_in_time = cursor.fetchone()[0]
        return labo_in_time

    def close(self):
        self.conn.close()

# らぼいん処理
def labo_in(user_id) -> str:
    success_flag = False #登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    start_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    lab = LabotterDatabase()
    # 初回登録時の処理
    if lab.check_exist_id(user_id) == 0: 
        lab.create_labo_row(user_id)
    # らぼりだ中ならば処理をする
    if lab.check_lab_in_flag(user_id) == False:        
        success_flag = lab.registory_labo_in(user_id, start_time)
    lab.close()
    return success_flag, start_time

# らぼりだ処理
def labo_rida(user_id) -> str:
    success_flag = False #登録処理管理用のフラグ。成功したらTrueにする
    dt_now = datetime.datetime.now()
    dt = 0
    end_time = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    lab = LabotterDatabase()
    # 初回登録時の処理
    if lab.check_exist_id(user_id) == 0: 
        lab.create_labo_row(user_id)
    # らぼいん中ならば処理をする
    if lab.check_lab_in_flag(user_id) == True:
        labo_in_time = str(lab.get_labo_in_time(user_id))
        start_time = datetime.datetime.strptime(labo_in_time, '%Y-%m-%d %H:%M:%S')
        dt = dt_now - start_time
        success_flag = lab.registory_labo_rida(user_id, end_time)
    lab.close()
    return success_flag, start_time, end_time, dt