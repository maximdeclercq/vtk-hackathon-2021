import json

import arrow
import scrapy
import base64
from bs4 import BeautifulSoup


class DummyOtaRatesSpider(scrapy.Spider):
    """ scrapy crawl ota_rates -o rates.json """
    name = "ota_rates"

    breakfast_included_strings = [
        "Breakfast included: Yes",
        "Included free breakfast",
        "With breakfast",
        "All meals are inclusive",
    ]
    breakfast_excluded_strings = [
        "Breakfast included: No",
        "Does not include free breakfast",
        "No free breakfast included",
        "No breakfast",
        "Breakfast at additional cost",
    ]

    refundable_strings = [
        "Refundable: Yes",
        "Refundable",
        "Free cancellation",
        "Can be cancelled free of charge",
    ]
    non_refundable_strings = [
        "Non-Refundable",
        "No Free cancellation",
        "Can not be cancelled free of charge",
        "Cancellation incurs a fee",
        "Refundable: No",
    ]

    # def start_requests(self):
    #     yield scrapy.Request(
    #         url="http://localhost:8282/rates/London/1013657/?&destination=London&arrivalDate=2019-11-15&departureDate=2019-11-16&numPersons=2",
    #         callback=self.parse
    #     )

    def start_requests(self):
        url_template = 'http://localhost:8282/rates/{destination_id}/{hotel_id}/?&page=1&destination=Amsterdam&arrivalDate={from_date}&departureDate={to_date}&numPersons=2'
        with open('hotels.json') as f:
            hotels = json.load(f)

        for hotel in hotels:
            start_date = arrow.get('2019-11-01')
            end_date = arrow.get('2020-12-31')
            for from_date in arrow.Arrow.range('day', start_date, end_date):
                if hotel["destination"] == "Brussels":
                    url = url_template.format(destination_id=hotel["destination"], hotel_id=hotel["hotel_id"], from_date=from_date.format('YYYY-MM-DD'), to_date=from_date.shift(days=1).format('YYYY-MM-DD'))
                    path = url[len('http://localhost:8282'):]
                    b64encodedPath = base64.b64encode(path.encode("utf-8")).decode()

                    yield scrapy.Request(
                        url=url_template.format(destination_id=hotel["destination"], hotel_id=hotel["hotel_id"], from_date=from_date.format('YYYY-MM-DD'), to_date=from_date.shift(days=1).format('YYYY-MM-DD')),
                        callback=self.parse,
                        cookies={'controlid': b64encodedPath},
                    )
                else:
                    yield scrapy.Request(
                        url=url_template.format(destination_id=hotel["destination"], hotel_id=hotel["hotel_id"], from_date=from_date.format('YYYY-MM-DD'), to_date=from_date.shift(days=1).format('YYYY-MM-DD')),
                        callback=self.parse
                    )

    def parse(self, response):
        # params
        prefix_length = len('http://localhost:8282/rates/')
        destination = response.url[prefix_length:].split('/')[0]

        param_info = response.css('.search-params').css('div::text').getall()
        arrival_date = param_info[3]
        departure_date = param_info[7]

        if destination == 'London':
            # London requires beautiful soup
            hotel_info = response.css('div.hotel-card-body')[0].css('table')
            hotel_id = hotel_info.css('td::text').getall()[2]

            soup = BeautifulSoup(response.text, 'html5lib')
            hotel_id = soup.table.find_all('tr')[2].find('td').string

            rate_properties = soup.find(id="rates-info").find('table').find_all('tr')
            room_name = rate_properties[0].text.split(": ")[1].strip()

            if 'Sold OUT' in room_name:
                return
            else:
                price_info = rate_properties[1].text.split(": ")[1]
                currency, _, amount = price_info.partition(' ')

                breakfast_included = rate_properties[2].text.strip() in self.breakfast_included_strings
                refundable = rate_properties[3].text.strip() in self.refundable_strings
                number_guests = rate_properties[4].text.split(": ")[1]

        else:
            # hotel info
            hotel_info = response.css('div.hotel-card-body')[0]
            hotel_id = hotel_info.css('p::text').get()

            # rate info
            rate_properties = response.css('div.rate-card-body')[0].css('.list-group-item::text').getall()
            room_name = rate_properties[0].split(": ")[1]

            if 'Sold OUT' in room_name:
                return
            else:
                price_info = rate_properties[1].split(": ")[1]
                currency, _, amount = price_info.partition(' ')


                breakfast_included = rate_properties[2].strip() in self.breakfast_included_strings
                refundable = rate_properties[3].strip() in self.refundable_strings
                number_guests = rate_properties[4].split(": ")[1]

        yield {
            'arrival_date': arrival_date,
            'departure_date': departure_date,
            'hotel_id': hotel_id,
            'room_name': room_name,
            'currency': currency,
            'amount': amount,
            'breakfast_included': breakfast_included,
            'refundable': refundable,
            'number_guests': number_guests,
        }
