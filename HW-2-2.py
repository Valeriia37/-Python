# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше
# введённой суммы (необходимо анализировать оба поля зарплаты).
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['vacancy_db']
vacancy = db.vacancy

currency_dict = {1: 'USD', 2: 'руб.'}
while True:
    salary = input('Введите минимальную заработную плату для поиска: ')
    currency = input('Введите валюту: \n1 для USD, \n2 для руб.\n')
    try:
        salary = int(salary)
        currency = int(currency)
        if currency > 2 or currency < 1:
            print('Вы ввдени не верное значение для валюты')
            continue
        break
    except ValueError:
        print('Вы ввели некорректное значение.')


for doc in vacancy.find({'$or': [
    {'min_salary': {'$gte': salary}, 'max_salary': None, 'salary_currency': currency_dict[currency]},
    {'max_salary': {'$gte': salary}, 'salary_currency': currency_dict[currency]}
]}):
    pprint(doc)
