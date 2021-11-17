import json

import arrow
import scrapy
from bs4 import BeautifulSoup

server_location = 'http://35.233.25.116'

server_location = 'http://localhost:8282'


class DummyOtaRatesSpider(scrapy.Spider):
    """ scrapy crawl ota_rates -o rates.json """
    name = "ota_rates"

    breakfast_included_strings = [
        "Breakfast included: Yes",
        "Included free breakfast",
        "With breakfast",
        "All meals are inclusive",
        "✅ Breakfast",
    ]
    breakfast_excluded_strings = [
        "Breakfast included: No",
        "Does not include free breakfast",
        "No free breakfast included",
        "No breakfast",
        "Breakfast at additional cost",
        "❌ Breakfast",
    ]

    refundable_strings = [
        "Refundable: Yes",
        "Refundable",
        "Free cancellation",
        "Can be cancelled free of charge",
        "No fee upon cancellation",
    ]
    non_refundable_strings = [
        "Refundable: No",
        "Non-Refundable",
        "No Free cancellation",
        "Can not be cancelled free of charge",
        "Cancellation incurs a fee",
    ]

    def start_requests(self):
        url_template = server_location + '/rates/{destination_id}/{hotel_id}/?&page=1&destination={destination_id}&arrivalDate={from_date}&departureDate={to_date}&numPersons={num_persons}'

        # Load all scraped hotels
        input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/hotels.json'

        with open(input_file) as f:
            all_hotels = json.load(f)

        # Loop over hotels
        for hotel in all_hotels:
            if hotel['destination'] != 'Berlin':
                continue
            # if hotel['hotel_id'] != '10064':
            #     continue
            # Loop over start dates
            start_date = arrow.get('2021-11-18')
            end_date = arrow.get('2022-02-01')
            for from_date in list(arrow.Arrow.range('day', start_date, end_date)):
                # Request LOS 1 and 2
                for los in [1, 2]:
                    # Persons
                    for num_persons in [1, 2]:
                        yield scrapy.Request(
                            url=url_template.format(destination_id=hotel["destination"], hotel_id=hotel["hotel_id"], from_date=from_date.format('YYYY-MM-DD'), to_date=from_date.shift(days=los).format('YYYY-MM-DD'), num_persons=num_persons),
                            callback=self.parse
                        )

    def parse(self, response):
        # params
        prefix_length = len(f'{server_location}/rates/')
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

            if 'sold out' in room_name.lower():
                return

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
            room_name = rate_properties[0].split(": ")[1].strip()

            if 'sold out' in room_name.lower():
                return

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
            'destination': destination,
        }
