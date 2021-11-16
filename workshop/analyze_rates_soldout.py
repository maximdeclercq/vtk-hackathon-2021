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
    # print(f'Got {len(rates)} rates')

    # values = []

    # for r in rates:
    #     values.append(float(r['amount']))

    # values = sorted(values)

    # print('min value', values[0])
    # print('mean value', statistics.mean(values))
    # print('max value', values[-1])

    # refundable = 0
    # nonrefundable = 0

    # withmeal = 0
    # withoutmeal = 0

    # for r in rates:
    #     if r['breakfast_included']:
    #         withmeal +=1
    #     else:
    #         withoutmeal += 1

    #     if r['refundable']:
    #         refundable += 1
    #     else:
    #         nonrefundable += 1

    # print('refundable', refundable, 'non-refundable', nonrefundable, 'percentage refundable', '{:.2f}%'.format(100 * float(refundable) / float(refundable + nonrefundable)))
    # print('with meal', withmeal, 'without meal', withoutmeal, 'percentage with meal', '{:.2f}%'.format(100 * float(withmeal) / float(withmeal + withoutmeal)))
    # print()
