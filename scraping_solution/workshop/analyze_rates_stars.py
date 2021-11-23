import json
import arrow
import math
import statistics
from collections import defaultdict

for city in ['Amsterdam', 'Paris', 'Brussels', 'London', 'Berlin']:
    print(city)

    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/hotels.json'

    with open(input_file) as f:
        hotels = json.load(f)

    hotel_id_to_stars = {h['hotel_id']:h['stars'] for h in hotels if h['destination'] == city and h['stars']}

    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/rates_{city.lower()}.json'

    with open(input_file) as f:
        rates = json.load(f)

    rates_per_star = defaultdict(list)

    for r in rates:
        price_per_person_per_night = float(r['amount']) / float(r['number_guests']) / abs((arrow.get(r['departure_date']) - arrow.get(r['arrival_date'])).days)
        r['ppn'] = price_per_person_per_night

    for r in rates:
        if rate_star_rating := hotel_id_to_stars.get(r['hotel_id']):
            rates_per_star[rate_star_rating].append(r['ppn'])

    for num_stars, rates in sorted(rates_per_star.items()):
        print(num_stars, statistics.mean(rates))
    print()
