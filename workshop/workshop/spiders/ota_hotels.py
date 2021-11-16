import scrapy

server_location = 'http://35.233.25.116'

# server_location = 'http://localhost:8282'


class DummyOtaHotelsSpider(scrapy.Spider):
    """ scrapy crawl ota_hotels -o hotels.json """
    name = "ota_hotels"

    # Skeleton implementation

    # def start_requests(self):
    #     yield scrapy.Request(url='https://www.google.com/', callback=self.parse_function)

    # def parse_function(self, response):
    #     yield {"Success": True}


    # Actual implementation

    def start_requests(self):
        urls = [
            f'{server_location}/sitemap/hotels/Amsterdam/?page=1',
            f'{server_location}/sitemap/hotels/Paris/?page=1',
            f'{server_location}/sitemap/hotels/London/?page=1',
            f'{server_location}/sitemap/hotels/Brussels/?page=1',
            f'{server_location}/sitemap/hotels/Berlin/?page=1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        # import ipdb; ipdb.set_trace()

        # Yield request to every hotel in the list on the page
        hotel_ids = response.css('li[hidden]::text').getall()
        prefix_length = len(f'{server_location}/sitemap/hotels/')
        destination = response.url[prefix_length:].split('/')[0]

        for hotel_id in hotel_ids:
            hotel_page = f'{server_location}/hotel/{destination}/{hotel_id}/'
            yield scrapy.Request(hotel_page, callback=self.parse_hotelpage)

        # Yield next pagination urls
        pagination_links = response.css('.pagination .page-item a::attr(href)').getall()
        next_page = pagination_links[-1]
        next_page_url = response.urljoin(next_page)
        yield scrapy.Request(next_page_url, callback=self.parse_list)

    def parse_hotelpage(self, response):
        # import ipdb; ipdb.set_trace()
        prefix_length = len(f'{server_location}/hotel/')
        destination = response.url[prefix_length:].split('/')[0]
        hotel_id = response.url[prefix_length:].split('/')[1]

        if destination in ['Amsterdam']:
            card = response.css('.hotel-card-body')

            title = card.css('h5::text').get()
            hotel_name, _, rooms_part = title.partition(' [')

            try:
                num_rooms = int(rooms_part.split(' ')[0])
            except:
                num_rooms = None

            card_texts = card.css('p').css('.card-text').getall()
            coordinates = card_texts[1]
            coordinates_text_parts = coordinates.split('Coordinates: ')[1].split('</small>')[0].split(', ')
            latitude = float(coordinates_text_parts[0].split(' ')[1])
            longitude = float(coordinates_text_parts[1].split(' ')[1])

            stars_html = card_texts[2]
            stars_text = stars_html.replace('<p class="card-text"><small class="text-muted">', '').replace('</small></p>', '')
            stars = int(stars_text.split(' ')[3])

        elif destination in ['Brussels', 'Paris', 'Berlin']:
            card = response.css('.hotel-card-body')

            title = card.css('h5::text').get()
            hotel_name, _, _ = title.partition('*')

            card_texts = card.css('p').css('.card-text').getall()
            coordinates = card_texts[1]
            coordinates_text_parts = coordinates.split('Coordinates: ')[1].split('</small>')[0].split(', ')
            latitude = float(coordinates_text_parts[0].split(' ')[1])
            longitude = float(coordinates_text_parts[1].split(' ')[1])

            stars = int(title.count('*'))

            try:
                num_rooms = int(card_texts[2].split('There are ')[1].split(' rooms')[0])
            except:
                num_rooms = None
        elif destination in ['London']:
            card = response.css('.hotel-card-body')

            title = card.css('h5::text').get()
            hotel_name, _, _ = title.partition(' [')

            card_texts = card.css('p').css('.card-text').getall()
            coordinates = card_texts[1]
            coordinates_text_parts = coordinates.split('Coordinates: ')[1].split('</small>')[0].split(', ')
            latitude = float(coordinates_text_parts[0].split(' ')[1])
            longitude = float(coordinates_text_parts[1].split(' ')[1])

            try:
                num_rooms = int(card_texts[2].split('There are ')[1].split(' rooms')[0])
            except:
                num_rooms = None

            try:
                stars_html = card_texts[3]
                stars_text = stars_html.replace('<p class="card-text"><small class="text-muted">', '').replace('</small></p>', '')
                stars = int(stars_text.split(' ')[3])
            except:
                stars = None

        else:
            return

        yield {
            'hotel_name': hotel_name,
            'num_rooms': num_rooms,
            'hotel_id': hotel_id,
            'latitude': latitude,
            'longitude': longitude,
            'destination': destination,
            'stars': stars,
        }