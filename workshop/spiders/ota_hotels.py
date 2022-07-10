import re
from base64 import b64encode
from urllib.parse import quote

import scrapy

from workshop.items import HotelItem

server_location = 'http://35.233.25.116'


class OtaHotelsSpider(scrapy.Spider):
    """ scrapy crawl ota -o all.json """
    name = "ota_hotels"
    start_urls = [server_location]

    def __init__(self, destination=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.destination = destination

    def parse(self, response, **kwargs):
        if sitemap_url := response.xpath("//a[contains(text(), 'Sitemap')]/@href").get():
            yield response.follow(sitemap_url, self.parse_sitemap)

    def parse_sitemap(self, response, **kwargs):
        for location in response.xpath("//h3[contains(text(), 'Available locations')]/../..//a"):
            name = location.xpath("./text()").get()
            url = location.xpath("./@href").get()
            if self.destination and name != self.destination:
                continue
            yield response.follow(url, self.parse_destination, meta={"destination": name})

    def parse_destination(self, response, **kwargs):
        for hotel in response.xpath("//h3[contains(text(), 'Available hotels')]/../..//a[contains(@class, 'hotellink')]"):
            name = hotel.xpath("./text()").get()
            url = hotel.xpath("./@href").get()
            hotel_id = re.search(fr"{response.meta['destination']}/([0-9]+)/", url).group(1)
            hotel = HotelItem(id=hotel_id, name=name, destination=response.meta["destination"])
            controlid = b64encode(quote(url).encode("utf-8"))
            yield response.follow(url, self.parse_hotel, meta={"hotel": hotel}, cookies={"controlid": controlid})
        if next_page := response.xpath("//a[contains(text(), 'Next')]/@href").get():
            yield response.follow(next_page, self.parse_destination, meta=response.meta)

    def parse_hotel(self, response, **kwargs):
        e = response.xpath("//div[contains(@class, 'hotel-card-body')]")[0]
        hotel: HotelItem = response.meta["hotel"]
        # Rooms
        if rooms_text := e.xpath(".//*[contains(text(), 'rooms')]").get():
            hotel["rooms"] = int(re.search(r"([0-9]+) rooms", rooms_text).group(1))
        # # Address
        # hotel.address = re.search(r"([0-9]+) rooms", e.xpath("./h5").get()).group(1)
        # Coords
        coordinates_text = e.xpath("./p/small[contains(text(), 'Coordinates')]/text()").get()
        coordinates = re.search(r"Lat (-?[0-9.]+), Long (-?[0-9.]+)", coordinates_text)
        hotel["latitude"] = float(coordinates.group(1))
        hotel["longitude"] = float(coordinates.group(2))
        # Stars
        if stars_text := e.xpath("./p/small[contains(text(), 'stars')]/text()").get():
            stars = re.search(r"([0-9.]+) stars", stars_text)
            hotel["stars"] = int(stars.group(1))
        elif stars_text := e.xpath("./h5[contains(text(), '*')]/text()").get():
            hotel["stars"] = stars_text.count("*")
        yield hotel



'''
    def parse(self, response, **kwargs):
        for hotel in response.xpath("//div[contains(@class, 'search-card')]"):
            name = hotel.xpath(".//h5[contains(@class, 'card-title')]/text()").get()
            stars = int(hotel.xpath(".//small[contains(text(), 'stars')]/text()").get().split(" ")[0])
            yield {"name": name, "stars": stars}


'''