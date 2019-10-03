import scrapy


class DummyOtaHotelsSpider(scrapy.Spider):
    """ scrapy crawl dummy_ota_hotels -o hotels.json """
    name = "dummy_ota_hotels"

    def start_requests(self):
        urls = [
            'http://localhost:8282/sitemap/?page=1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pagination_links = response.css('.pagination .page-item a::attr(href)').getall()
        next_page = pagination_links[-1]
        next_page_url = response.urljoin(next_page)
        yield scrapy.Request(next_page_url, callback=self.parse)

        ids = response.css('li[hidden]::text').getall()
        yield {
            'ids': ids
        }
