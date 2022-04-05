# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# которая будет добавлять только новые вакансии/продукты в вашу базу.
import json
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pprint import pprint


def get_response_dom(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.ok:
        return bs(response.text, 'html.parser')
    else:
        print(f'Response on {response.url} finished with {response.status_code} status_code.')
        return bs(response.text, 'html.parser')


def get_max_page_num(dom):
    '''
    Получение максимального значения страниц ао запросу
    :return: int
    '''
    if not dom.find('a', {'data-qa': 'pager-next'}):
        return 1
    pages = dom.find('div', {'class': 'pager'})
    buttons_list = pages.findChildren(recursive=False)
    page = buttons_list[-2].getText().strip('.')
    try:
        last_page = int(page)
        return last_page
    except ValueError:
        print(f'Ошибка нахождеия максимального значения страниц. Получено - {page}')


def write_to_database(vac):
    '''
    Записывает словарь информации о вакансии в базу данных
    :param vac: словарь
    '''
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancy_db']
    vacancy = db.vacancy
    if vacancy.find_one({'link': vac['link']}):
        print(f'Duplicated vacancy {vac["link"]}')
    else:
        vacancy.insert_one(vac)
        print(f'Success insert the link {vac["link"]}')


def hh_get_vacancy_info(dom, to_write=True):
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
    site = 'https://hh.ru'
    vacancies_list = []
    for vacancy in vacancies:
        vacancy_data = {}
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
        vacancy_company_name = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')
        try:
            vacancy_company_link = site + vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})['href']
        except TypeError:
            vacancy_company_link = None
        vacancy_data['site'] = site
        vacancy_data['title'] = vacancy_title
        vacancy_data['city'] = vacancy_city
        vacancy_data['company_name'] = vacancy_company_name
        vacancy_data['company_link'] = vacancy_company_link
        vacancy_data['min_salary'] = vacancy_salary_min
        vacancy_data['max_salary'] = vacancy_salary_max
        vacancy_data['salary_currency'] = vacancy_salary_currency
        vacancy_data['link'] = vacancy_link

        if to_write:
            write_to_database(vacancy_data)
        vacancies_list.append(vacancy_data)
    return vacancies_list


def vacancy_search(vacancy_name):
    base_url = 'https://hh.ru'
    url = f'{base_url}/search/vacancy?clusters=true&no_magic=true&ored_clusters=true&items_on_page={20}&enable_snippets=true&salary=&text={vacancy_name}'
    vacancies_list = []

    dom = get_response_dom(url)
    max_page = get_max_page_num(dom)
    indiv_page = input(f'Сколько из {max_page} доступных страниц хотите обработать? ')
    try:
        indiv_page = int(indiv_page)
    except ValueError:
        print('Введено некоректное значение, будут обработаны все страницы')
        indiv_page = max_page
    if indiv_page > max_page:
        indiv_page = max_page

    i = 1
    while i <= indiv_page:
        vacancies_list.append(hh_get_vacancy_info(dom))
        if dom.find('a', {'data-qa': 'pager-next'}):
            url = base_url + dom.find('a', {'data-qa': 'pager-next'})['href']
            dom = get_response_dom(url)
            i += 1
        else:
            break
    return vacancies_list

#
# with open('vacancy_data.json', 'r', encoding='utf-8') as f:
#     vacancy_list = json.load(f)
#
# for vacancies in vacancy_list:
#     for vac in vacancies:
#         write_to_database(vac)

vacancy_name = input('Введите должность для поиска: ')
vacancy_list = vacancy_search(vacancy_name)
pprint(vacancy_list)
