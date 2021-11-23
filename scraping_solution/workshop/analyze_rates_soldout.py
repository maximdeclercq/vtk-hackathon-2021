import json
import math
import statistics
from collections import defaultdict

for city in ['Amsterdam', 'Paris', 'Brussels', 'London', 'Berlin']:

    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/hotels.json'

    with open(input_file) as f:
        hotels = json.load(f)

    all_hotels = set(h['hotel_id'] for h in hotels if h['destination'] == city)

    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/rates_{city.lower()}.json'

    print(city)

    with open(input_file) as f:
        rates = json.load(f)

    hotels_with_rate_on_christmas = set()

    for r in rates:
        if r["arrival_date"] == "2021-12-25":
            hotels_with_rate_on_christmas.add(r['hotel_id'])


    print('Amount of hotels with availability', len(hotels_with_rate_on_christmas), ', percentage', '{:.2f}%'.format(100*len(hotels_with_rate_on_christmas) / len(all_hotels)))
