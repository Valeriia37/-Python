# Посмотреть документацию к API GitHub, разобраться как вывести список наименований репозиториев
# для конкретного пользователя, сохранить JSON-вывод в файле *.json.
import json
import requests
from pprint import pprint

url = 'https://api.github.com/users/'
name = 'Valeriia37'
# name = 'MityaSorokin'

response = requests.get(url + name + '/repos', verify=False)
if response.ok:
    j_data = response.json()
    repo_list = []
    for item in j_data:
        repo_list.append(item['name'])
    with open(f"{name}_repo_list.json", 'a') as file:
        json.dump(j_data, file)
    print(repo_list)
else:
    print('Что-то пошло не так')

