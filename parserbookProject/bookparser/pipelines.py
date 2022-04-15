# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class BookparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        if spider.name == 'book24':
            item['rating'] = float(item['rating'].strip().replace(',', '.'))
            if len(item['name'].split(':')) == 2:
                author, item['name'] = item['name'].split(':')
                item['authors'] = author.split(',')
            item['name'] = item['name'].strip()
            item['old_price'], item['new_price'] = self.book_24_prices(item['old_price'], item['new_price'])
        if spider.name == 'labirint':
            if len(item['name'].split(':')) == 2:
                item['name'] = item['name'].split(":")[1]
            if item['old_price']:
                item['old_price'] = int(item['old_price'])
            item['new_price'] = int(item['new_price'])
            item['rating'] = float(item['rating'])
        collection = self.mongobase[spider.name]
        if collection.find_one({'link': item['url']}):
            print(f'Duplicated item {item["url"]}')
        else:
            collection.insert_one(item)
            print(f'Success insert the link {item["url"]}')
        return item

    def book_24_prices(self, old_price, new_price):
        if new_price:
            new_price, _ = new_price.replace('\xa0', '').split()
            new_price = int(new_price)
        if old_price:
            old_price, _ = old_price.replace('\xa0', '').split()
            old_price = int(old_price)
        return old_price, new_price