import scrapy


class DummyOtaHotelsSpider(scrapy.Spider):
    """ scrapy crawl dummy_ota_hotels -o hotels.json """
    name = "dummy_ota_hotels"

    def start_requests(self):
        urls = [
            'http://localhost:8282/sitemap/hotels/Amsterdam/?page=1',
            'http://localhost:8282/sitemap/hotels/Paris/?page=1',
            'http://localhost:8282/sitemap/hotels/London/?page=1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        # Yield request to every hotel in the list on the page
        hotel_ids = response.css('li[hidden]::text').getall()
        prefix_length = len('http://localhost:8282/sitemap/hotels/')
        destination = response.url[prefix_length:].split('/')[0]

        for hotel_id in set(hotel_ids):
            hotel_page = f'http://localhost:8282/hotel/{destination}/{hotel_id}/'
            yield scrapy.Request(hotel_page, callback=self.parse_hotelpage)

        # Yield next pagination urls
        pagination_links = response.css('.pagination .page-item a::attr(href)').getall()
        next_page = pagination_links[-1]
        next_page_url = response.urljoin(next_page)
        yield scrapy.Request(next_page_url, callback=self.parse_list)

    def parse_hotelpage(self, response):
        prefix_length = len('http://localhost:8282/hotel/')
        destination = response.url[prefix_length:].split('/')[0]
        hotel_id = response.url[prefix_length:].split('/')[1]

        card = response.css('.hotel-card-body')

        title = card.css('h5::text').get()
        hotel_name, _, rooms_part = title.partition(' [')
        num_rooms = int(rooms_part.split(' ')[0])

        card_texts = card.css('p').css('.card-text').getall()
        currency_html = card_texts[3]
        currency_text = currency_html.replace('<p class="card-text"><small class="text-muted">', '').replace('</small></p>', '')
        currency = currency_text.split(' ')[1]

        stars_html = card_texts[2]
        stars_text = stars_html.replace('<p class="card-text"><small class="text-muted">', '').replace('</small></p>', '')
        stars = stars_text.split(' ')[0]

        yield {
            'hotel_name': hotel_name,
            'num_rooms': num_rooms,
            'hotel_id': hotel_id,
            'currency': currency,
            'destination': destination,
            'stars': stars,
        }