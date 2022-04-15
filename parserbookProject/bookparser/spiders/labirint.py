import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/genres/2532']
    base_url = 'https://www.labirint.ru'

    def parse(self, response: HtmlResponse):
        next_page = self.start_urls[0] + response.xpath('//div[@class="pagination-next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@class="product-title-link"]/@href').getall()
        links.append(response.xpath('//a[@class="b-product-block-link"]/@href').getall())
        for link in links:
            yield response.follow(self.base_url + link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        name = response.css('h1::text').get()
        authors = response.xpath('//div[@class="authors"]/a/text()').getall()
        old_price = response.xpath('//span[@class="buying-priceold-val-number"]/text()').get()
        new_price = response.xpath('//span[@class="buying-pricenew-val-number"]/text() | //span[@class="buying-price-val-number"]/text()').get()
        rating = response.xpath('//div[@id="rate"]/text()').get()
        url = response.url
        yield BookparserItem(name=name, authors=authors, old_price=old_price,
                             new_price=new_price, rating=rating, url=url)
        print()
