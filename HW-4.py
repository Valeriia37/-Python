'''
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru,
lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
'''
import requests
import datetime
from pymongo import MongoClient
from lxml import html
from pprint import pprint

def write_to_database(news):
    '''
    Записывает словарь информации о новостях в базу данных
    :param news: словарь
    '''
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancy_db']
    news_data = db.news
    if news_data.find_one({'link': news['link']}):
        print(f'Duplicated news {news["link"]}')
    else:
        news_data.insert_one(news)
        print(f'Success insert the link {news["link"]}')

def get_response_dom(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)
    return dom

def time_format(time):
    """
    Форматирование даты.
    :param time: изначальные данные
    :return: приведение к формату YYYY-MM-DD hh:mm
    Так как работала только с сегодняшними новостями, то обрабатывала только их.
    Как только будут другие потребности запроса, можно будет дописать
    """
    if len(time) == 5:
        time = str(datetime.datetime.today().strftime('%Y-%m-%d ')) + time
    return time

def lenta_news(dom, to_write=True):
    url = 'https://lenta.ru'
    news_list = []
    top_news = dom.xpath('//div[@class="topnews__first-topic"]')[0]
    new_cards = dom.xpath("//a[@class='card-mini _topnews']")
    new_cards.append(top_news)
    for news in new_cards:
        new_data = {}
        if news.xpath(".//a/@class"):
            link = top_news.xpath(".//a/@href")[0]
            title = top_news.xpath(".//h3/text()")[0]
            time = top_news.xpath(".//time[@class='card-big__date']/text()")[0]
        else:
            link = news.xpath("./@href")[0]
            title = news.xpath(".//span[@class='card-mini__title']/text()")[0]
            time = news.xpath(".//time[@class='card-mini__date']/text()")[0]

        if link[0] == '/':
            link = url + link
        time = time_format(time)

        new_data['link'] = link
        new_data['title'] = title
        new_data['time'] = time
        new_data['resource'] = 'Lenta.ru'

        if to_write:
            write_to_database(new_data)

        news_list.append(new_data)
    return news_list


def mail_news(dom, to_write=True):
    main_container = dom.xpath('//div[@data-logger="news__MainTopNews"]')[0]
    links = main_container.xpath(".//td[@class='daynews__items']//a/@href")
    links.extend(main_container.xpath(".//td[@class='daynews__main']//a/@href"))
    links.extend(main_container.xpath(".//li[@class='list__item']/a/@href"))
    news_list = []
    for link in links:
        news_data = {}
        dom = get_response_dom(link)
        resource = dom.xpath("//a[contains(@class,'breadcrumbs__link')]/span/text()")[0]
        title = dom.xpath("//h1[@class='hdr__inner']/text()")[0]
        time = dom.xpath("//span[@class='breadcrumbs__item']//span[@datetime]/@datetime")[0].replace('T', ' ')[:16]
        news_data['link'] = link
        news_data['title'] = title
        news_data['time'] = time
        news_data['resource'] = resource

        if to_write:
            write_to_database(news_data)

        news_list.append(news_data)
    return news_list

def yandex_news(dom, to_write=True):
    containers = dom.xpath("//div[contains(@class, 'news-top-flexible-stories ')]/div")
    news_list = []
    for news in containers:
        news_data = {}
        links = news.xpath(".//a")
        title = links[0].xpath("./text()")[0].replace('\xa0', ' ')
        link = links[0].xpath("./@href")[0]
        time = news.xpath(".//span/text()")[0]
        time = time_format(time)
        resource = links[1].xpath("./text()")[0]
        news_data['link'] = link
        news_data['title'] = title
        news_data['time'] = time
        news_data['resource'] = resource

        if to_write:
            write_to_database(news_data)
        news_list.append(news_data)
    return news_list

def search_news(*arg):
    news_list = []
    for site_name in arg:
        if 'mail' in site_name.lower():
            site = 'https://news.mail.ru/'
            dom = get_response_dom(site)
            news = mail_news(dom)
        if 'yandex' in site_name.lower():
            site = 'https://yandex.ru/news/'
            dom = get_response_dom(site)
            news = yandex_news(dom)
        if 'lenta' in site_name.lower():
            site = 'https://lenta.ru/'
            dom = get_response_dom(site)
            news = lenta_news(dom)
        else:
            print(f'{site_name} нет в базе данных.')
            news = None
        news_list.append(news)
    return news_list


pprint(search_news('yandex', 'mail', 'lenta'))
