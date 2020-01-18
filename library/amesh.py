# coding: utf-8
import requests
import slackbot_settings
import os
from pytz import timezone
from PIL import Image
from datetime import datetime

BASE_MAP_FILE = './image/map050.jpg'
MASK_MAP_FILE = './image/msk050.png'
SAVE_FILE_NAME = './image/map.png'

# 雨雲画像を取得する。
def get_map():
    timestamp = get_amesh_img_path()
    mesh_file = get_img_from_url('https://tokyo-ame.jwa.or.jp/mesh/100/' + timestamp + '.gif')
    amesh_file_without_cityname = generate_img(BASE_MAP_FILE, mesh_file)
    amesh_map = generate_img(amesh_file_without_cityname, MASK_MAP_FILE)
    # 圧縮する
    im1 = Image.open(amesh_map)
    im1.save(amesh_map, 'JPEG', quality=50)
    file = amesh_map
    # ダウンロードしたamesh画像を削除する
    os.remove(mesh_file)

    return amesh_map

def generate_img(base: str, top: str)-> str:
    im1 = Image.open(base)
    im2 = Image.open(top).convert('RGBA') # 上に載せる画像を透過指定する
    x, y = im1.size
    img_resize = im2.resize((x,y))
    im1.paste(img_resize,(0,0),img_resize.split()[3])
    im1.save(SAVE_FILE_NAME)
    return SAVE_FILE_NAME

def get_img_from_url(url: str) -> str:
    r = requests.get(url, stream = True)
    f_name = get_filename_from_url('./image/' + url)
    if r.status_code == 200:
        with open(f_name, 'wb') as f:
            f.write(r.content)
        return f_name

def get_amesh_img_path() -> str:
    now = int(datetime.now(timezone('Asia/Tokyo')).strftime('%Y%m%d%H%M'))
    now = now - (now % 5)
    return str(now)

def get_filename_from_url(url: str) -> str:
    tmp, path = url.rsplit("/",1)
    return path

def main():
    amesh_map_file_path = get_map()

if __name__ == '__main__':
    main()
