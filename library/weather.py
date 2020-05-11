# coding: utf-8

import requests
import json
import xml.etree.ElementTree as ET


def get_city_id_from_city_name(city_name):
    city_id = None
    city_list_url = 'http://weather.livedoor.com/forecast/rss/primary_area.xml'
    response = requests.get(city_list_url)
    root = ET.fromstring(response.content)
    for city_list in root.iter('city'):
        city_title = str(city_list.get('title'))
        if city_name == city_title:
            city_id = city_list.get('id')
    return city_id


def get_weather(city_id):
    data = None
    weather_url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=' + \
        str(city_id)
    response = requests.get(weather_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data['description']['text']
    else:
        data = "天気情報の取得に失敗 code:" + str(response.status_code)
        return data


def main():
    print('Hello World')


if __name__ == '__main__':
    main()
