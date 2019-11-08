import scrapy
import json
import arrow


class DummyOtaRatesSpider(scrapy.Spider):
    """ scrapy crawl dummy_ota_rates -o rates.json """
    name = "dummy_ota_rates"

    def start_requests(self):
        url_template = 'http://localhost:8282/rates/{destination_id}/{hotel_id}/?&page=1&destination=Amsterdam&arrivalDate={from_date}&departureDate={to_date}&numPersons=2'
        with open('hotels.json') as f:
            hotels = json.load(f)

        for hotel in hotels:
            start_date = arrow.get('2019-11-01')
            end_date = arrow.get('2020-12-31')
            for from_date in arrow.Arrow.range('day', start_date, end_date):
                yield scrapy.Request(
                    url=url_template.format(destination_id=hotel["destination"], hotel_id=hotel["hotel_id"], from_date=from_date.format('YYYY-MM-DD'), to_date=from_date.shift(days=1).format('YYYY-MM-DD')),
                    callback=self.parse
                )

    def parse(self, response):
        # params
        param_info = response.css('.search-params').css('div::text').getall()
        arrival_date = param_info[3]
        departure_date = param_info[7]

        # hotel info
        hotel_info = response.css('div.hotel-card-body')[0]
        hotel_id = hotel_info.css('p::text').get()

        # rate info
        rate_properties = response.css('div.rate-card-body')[0].css('.list-group-item::text').getall()
        room_name = rate_properties[0].split(": ")[1]

        if 'Sold OUT' in room_name:
            # yield {
            #     'arrival_date': arrival_date,
            #     'departure_date': departure_date,
            #     'hotel_id': hotel_id,
            #     'soldout': True,
            # }
            pass
        else:
            price_info = rate_properties[1].split(": ")[1]
            currency, _, amount = price_info.partition(' ')

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

            breakfast_included = rate_properties[2].strip() in breakfast_included_strings
            refundable = rate_properties[3].strip() in refundable_strings
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
