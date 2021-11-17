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

    # week rate amounts, weekend rate amounts
    hotel_id_counts = {h['hotel_id']: [[], []] for h in hotels if h['destination'] == city}


    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/rates_{city.lower()}.json'

    with open(input_file) as f:
        rates = json.load(f)

    rates_per_star = defaultdict(list)

    for r in rates:
        if int(r['number_guests']) != 2 or abs((arrow.get(r['departure_date']) - arrow.get(r['arrival_date'])).days) != 1:
            continue

        if arrow.get(r['arrival_date']).weekday() not in [5, 6]:
            hotel_id_counts[r['hotel_id']][0].append(float(r['amount']))
        else:
            hotel_id_counts[r['hotel_id']][1].append(float(r['amount']))

    averages_by_hotel_id = {}
    for hotel_id, stats in list(hotel_id_counts.items()):
        if stats[0] and stats[1]:
            averages_by_hotel_id[hotel_id] = [statistics.mean(stats[0]), statistics.mean(stats[1])]

    week_more_expensive_count = 0
    weekend_more_expensive_count = 0

    for stats in averages_by_hotel_id.values():
        if stats[0] > stats[1]:
            week_more_expensive_count += 1
        else:
            weekend_more_expensive_count += 1

    print('week_more_expensive_count', week_more_expensive_count)
    print('weekend_more_expensive_count', weekend_more_expensive_count)
