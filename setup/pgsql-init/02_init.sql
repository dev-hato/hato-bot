CREATE TABLE IF NOT EXISTS vocabulary(no serial UNIQUE, word text);
CREATE TABLE IF NOT EXISTS labotter(user_name text UNIQUE, lab_in_flag int, lab_in timestamp, lab_rida timestamp, min_sum int);
