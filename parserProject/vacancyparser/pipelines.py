# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class VacancyparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.vacancy

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            clean_salary = self.hh_process_salary(item['salary'])
        else:
            clean_salary = self.sj_process_salary(item['salary'])
        item['min_salary'], item['max_salary'], item['currency'] = clean_salary
        del item['salary']
        collection = self.mongobase[spider.name]
        if collection.find_one({'link': item['url']}):
            print(f'Duplicated item {item["url"]}')
        else:
            collection.insert_one(item)
            print(f'Success insert the link {item["url"]}')
        return item

    def hh_process_salary(self, salary):
        for n, elem in enumerate(salary):
            salary[n] = elem.strip().replace("\xa0", '')
        if salary[0] == 'до':
            vacancy_salary_max = int(salary[1])
            vacancy_salary_min = None
            vacancy_salary_currency = salary[3]
        elif salary[0] == 'от':
            vacancy_salary_min = int(salary[1])
            if salary[2] == 'до':
                vacancy_salary_max = int(salary[3])
                vacancy_salary_currency = salary[5]
            else:
                vacancy_salary_max = None
                vacancy_salary_currency = salary[3]
        else:
            vacancy_salary_min = None
            vacancy_salary_max = None
            vacancy_salary_currency = None
        return vacancy_salary_min, vacancy_salary_max, vacancy_salary_currency

    def sj_process_salary(self, salary):
        for n, elem in enumerate(salary):
            salary[n] = elem.strip().replace("\xa0", '')
        if salary[0] == 'от':
            vacancy_salary_min = int(salary[2][:-4])
            vacancy_salary_max = None
            vacancy_salary_currency = salary[2][-4:]
        elif salary[0] == 'до':
            vacancy_salary_min = None
            vacancy_salary_max = int(salary[2][:-4])
            vacancy_salary_currency = salary[2][-4:]
        elif len(salary) > 4:
            vacancy_salary_min = int(salary[0])
            vacancy_salary_max = int(salary[4])
            vacancy_salary_currency = salary[6]
        elif len(salary) == 3:
            vacancy_salary_min = int(salary[0])
            vacancy_salary_max = int(salary[0])
            vacancy_salary_currency = salary[2]
        else:
            vacancy_salary_min = None
            vacancy_salary_max = None
            vacancy_salary_currency = None
        return vacancy_salary_min, vacancy_salary_max, vacancy_salary_currency