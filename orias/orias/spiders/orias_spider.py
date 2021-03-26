import scrapy


class OriasSpider(scrapy.Spider):
    name = "orias"

    start_urls = [
        'http://127.0.0.1:8000/consumption/125/2015'
    ]

    def parse(self, response):
        page = response.url.split('/')[-1]
        filename = 'posts-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
