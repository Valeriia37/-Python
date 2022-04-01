'''
Необходимо собрать информацию по продуктам питания с сайта: Список протестированных
продуктов на сайте Роскачество Приложение должно анализировать несколько страниц сайта
(вводим через input или аргументы).
Получившийся список должен содержать:

Наименование продукта.
Все параметры (Безопасность, Натуральность, Пищевая ценность, Качество) Не забываем
преобразовать к цифрам
Общую оценку
Сайт, откуда получена информация.
Общий результат можно вывести с помощью dataFrame через Pandas. Сохраните в json либо csv.
'''

import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs



base_url = 'https://rskrf.ru'
url = 'https://rskrf.ru/ratings/produkty-pitaniya/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

# Сбор ссылок на категории и подкатегории
response = requests.get(url, headers=headers)
with open('rskr_category.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
with open('rskr_category.html', 'r', encoding='utf-8') as f:
    category_html = f.read()

dom_categories = bs(category_html, 'html.parser')
categories = dom_categories.find_all('div', {'class': 'category-item'})
category_list = []
for category in categories:
    category_data = {}
    category_name = category.find('span', {'class': 'h5'}).getText()
    category_link = base_url + category.find('a')['href']
    subcategory_list = []
    response = requests.get(category_link, headers=headers)
    with open('rskr_subcategory.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    with open('rskr_subcategory.html', 'r', encoding='utf-8') as f:
        subcategory_html = f.read()
    dom_subcategory = bs(subcategory_html, 'html.parser')
    subcategories = dom_subcategory.find_all('div', {'class': 'category-item'})

    for subcategory in subcategories:
        subcategory_data = {}
        subcategory_name = subcategory.find('span', {'class': 'd-xl-block d-none'}).getText()
        subcategory_link = base_url + subcategory.find('a')['href']
        subcategory_data['subcategory'] = subcategory_name
        subcategory_data['subcategory_link'] = subcategory_link
        subcategory_list.append(subcategory_data)

    category_data['category'] = category_name
    category_data['category_link'] = category_link
    category_data['subcategory'] = subcategory_list
    category_list.append(category_data)

with open('rskr_categories_names.json', 'w', encoding='utf-8') as f:
    json.dump(category_list, f)



# Поучение нужной ссылки по запросу ввода
with open('rskr_categories_names.json', 'r', encoding='utf-8') as f:
    category_list = json.load(f)

while True:
    print("КАТЕГОРИИ: ")
    for category in category_list:
        print(f'- {category["category"]}')
    category_name = input('Выберете одну из следующих категорий, для выхода нажмите Enter: ')
    if not category_name:
        break
    print('ПОДКАТЕГОРИИ: ')
    for category in category_list:
        if category['category'] == category_name:
            subcategory_list = category['subcategory']
            for subcategory in subcategory_list:
                print(f'- {subcategory["subcategory"]}')
            break
    subcategory_name = input('Выберете одну из подкатегорий:')
    for subcategory in subcategory_list:
        if subcategory['subcategory'] == subcategory_name:
            url = subcategory['subcategory_link']
            print(url)
            break

'''
Пропущен шаг перехода с url подкатегории к url конкретного товара
'''


# Получение информации о продукте
url = 'https://rskrf.ru/goods/ikra-lososevaya-zernistaya-pervyy-sort-tunaycha/'
response_items = requests.get(url, headers=headers)
with open('rskr_tunaycha.html', 'w', encoding='utf-8') as f:
    f.write(response_items.text)
with open('rskr_tunaycha.html', 'r', encoding='utf-8') as f:
    items_html = f.read()

dom_items = bs(items_html, 'html.parser')
product_data = {}
product_data['product_title'] = dom_items.find('h1', {'class': 'product-title'}).getText().strip()
features = dom_items.find_all('div', {'class': 'rating-item'})
features_list = []
for feature in features:
    feature_data = {}
    feature_data['feature_name'] = feature.find('span').getText()
    feature_data['feature_rate'] = float(feature.find('div', {'class': 'starrating'}).getText().strip())
    features_list.append(feature_data)
product_data['features'] = features_list
product_data['link'] = url

with open('rskr_product_info.json', 'w', encoding='utf-8') as f:
    json.dump(product_data, f)
pprint(product_data)

