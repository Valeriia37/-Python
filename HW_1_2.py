# Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.
import json
import requests

from pprint import pprint

url = 'https://api.nasa.gov/planetary/apod?api_key='
api_key = 'dq9MhigobBBbg6ChPUkGFIAU64mAyfc9mPpR0BxY'
response = requests.get(url + api_key)

with open('nata_data.json', 'w') as file:
    json.dump(response.json(), file)

pprint(response.json())
