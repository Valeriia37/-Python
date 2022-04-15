from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from vacancyparser.spiders.hhru import HhruSpider
from vacancyparser.spiders.spjobru import SpjobruSpider

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(HhruSpider)
    runner.crawl(SpjobruSpider)

    reactor.run()