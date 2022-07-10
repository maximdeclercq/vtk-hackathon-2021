import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import scrapy

from workshop.items import RateItem, RoomItem

server_location = 'http://35.233.25.116'


class OtaHotelsSpider(scrapy.Spider):
    """ scrapy crawl ota -o all.json """
    name = "ota_rates"

    def __init__(self, destination=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.destination = destination

    def start_requests(self):
        today = datetime(2021, 12, 1)
        # today = datetime.now().date()
        for f in sorted(os.listdir(".")):
            if destination := next(iter(re.findall(r"hotels-(.*)\.json$", f)), None):
                destination = destination.title()
                if self.destination and destination != self.destination:
                    continue
                hotels = json.loads(Path(f).read_text())
                for hotel in hotels:
                    # Arrival in the next 100 days
                    for arrival in [today + timedelta(days=d) for d in range(100)]:
                        for departure in [arrival + timedelta(days=1), arrival + timedelta(days=2)]:
                            for persons in (1, 2):
                                args = {
                                    "destination": destination,
                                    "arrivalDate": arrival.strftime("%Y-%m-%d"),
                                    "departureDate": departure.strftime("%Y-%m-%d"),
                                    "numPersons": persons,
                                }
                                urlencode(args)
                                url = f"{server_location}/rates/{destination}/{hotel['id']}/?{urlencode(args)}"
                                rate = RateItem(destination=destination, hotel_id=hotel['id'], arrival=arrival, departure=departure, persons=persons)
                                yield scrapy.Request(url, self.parse, meta={"rate": rate})

    def parse(self, response, **kwargs):
        rate = response.meta["rate"]
        e = response.xpath("//div[contains(@class, 'rate-card-body')]")
        if len(e) > 1:
            raise Exception("Multiple rooms returned")
        e = e[0]
        name_text, price_text, breakfast_text, cancel_text, guest_text = e.xpath("./ul/li/text()")
        # Name
        name = name_text.get().split(":", 1)[-1].strip()
        # Price
        # price_text = e.xpath(".//*[contains(text(), 'Price')]/text()")
        price = float(re.search(r"([0-9]+\.[0-9]+)", price_text.get()).group(1))
        # Guests
        guests = int(re.search(r"([0-9]+)", guest_text.get()).group(1))
        # Room
        rate["room"] = RoomItem(name=name, price=price, breakfast=breakfast_text.get(), refundable=cancel_text.get(), max_persons=guests)
        yield rate