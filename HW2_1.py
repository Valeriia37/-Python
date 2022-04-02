# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через
# аргументы получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение
# должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура
# должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame
# через pandas. Сохраните в json либо csv.
import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs


def vacancy_search(vacancy_name):
    base_url = 'https://hh.ru'
    url = base_url + '/search/vacancy?search_field=name&search_field=company_name&search_field=description'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    params = {'text': vacancy_name}
    vacancies_list = []

    i = 1
    while url and i <= 20:
        if i == 1:
            response = requests.get(url, headers=headers, params=params)
        else:
            response = requests.get(url, headers=headers)
        with open('last_requests.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        with open('last_requests.html', 'r', encoding='utf-8') as f:
            html_file = f.read()
        dom = bs(html_file, 'html.parser')
        vacancies_list.append(hh_get_vacancy_info(dom))
        if dom.find('a', {'data-qa': 'pager-next'}):
            url = base_url + dom.find('a', {'data-qa': 'pager-next'})['href']
        else:
            url = None
        i += 1
    with open('vacancy_data.json', 'a', encoding='utf-8') as f:
        json.dump(vacancies_list, f)
    return vacancies_list

def hh_get_vacancy_info(dom):
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
    vacancies_list = []
    for vacancy in vacancies:
        vacancy_data = {}
        vacancy_site = 'https://hh.ru'
        vacancy_title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
        vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if vacancy_salary:
            vacancy_salary_list = vacancy_salary.getText().replace('\u202f', '').replace('–', '').split()
            if vacancy_salary_list[0] == 'до':
                vacancy_salary_max = int(vacancy_salary_list[1])
                vacancy_salary_min = None
            elif vacancy_salary_list[0] == 'от':
                vacancy_salary_min = int(vacancy_salary_list[1])
                vacancy_salary_max = None
            else:
                vacancy_salary_min = int(vacancy_salary_list[0])
                vacancy_salary_max = int(vacancy_salary_list[1])
            vacancy_salary_currency = vacancy_salary_list[2]
        else:
            vacancy_salary_min = None
            vacancy_salary_max = None
            vacancy_salary_currency = None
        vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
        vacancy_city = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText().rstrip(',')
        vacancy_company_name = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText()
        vacancy_company_link = vacancy_site + vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})['href']
        vacancy_data['site'] = vacancy_site
        vacancy_data['title'] = vacancy_title
        vacancy_data['city'] = vacancy_city
        vacancy_data['company_name'] = vacancy_company_name
        vacancy_data['company_link'] = vacancy_company_link
        vacancy_data['min_salary'] = vacancy_salary_min
        vacancy_data['max_salary'] = vacancy_salary_max
        vacancy_data['salary_currency'] = vacancy_salary_currency
        vacancy_data['link'] = vacancy_link
        pprint(vacancy_data)
        vacancies_list.append(vacancy_data)
    return vacancies_list


vacancy_name = input('Введите должность для поиска: ')
vacancy_list = vacancy_search(vacancy_name)

pprint(vacancy_list)


