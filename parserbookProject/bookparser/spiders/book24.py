import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/catalog/zarubezhnye-detektivy-2045/']

    def parse(self, response: HtmlResponse):
        # почему-то ссылка не работает, но в браузере xpath находит такой путь
        next_page = response.xpath('//a[contains(@class, "_next")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[contains(@class, 'product-card__name ')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parser)

    def book_parser(self, response: HtmlResponse):
        name = response.css('h1::text').get()
        authors = response.xpath("//div[@class='product-characteristic__value']/a[contains(@href, 'author')]/text()").get()
        old_price = response.xpath("//span[contains(@class, 'product-sidebar-price__price-old')]/text()").get()
        new_price = response.xpath("//span[@class='app-price product-sidebar-price__price']/text()").get()
        rating = response.xpath("//span[@class='rating-widget__main-text']/text()").get()
        url = response.url
        yield BookparserItem(name=name, authors=authors, old_price=old_price,
                             new_price=new_price, rating=rating, url=url)
        print()
