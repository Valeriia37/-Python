import scrapy
from vacancyparser.items import VacancyparserItem
from scrapy.http import HtmlResponse

class SpjobruSpider(scrapy.Spider):
    name = 'spjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&noGeo=1&page=1']

    def parse(self, response: HtmlResponse):
        # response.status
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[contains(@class, '_1IHWd _2b9za')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css("h1::text").get()
        salary = response.xpath("//span[contains(@class, '_2eYAG -gENC _1TcZY dAWx1')]//text()").getall()
        url = response.url
        yield VacancyparserItem(name=name, salary=salary, url=url)
        print()