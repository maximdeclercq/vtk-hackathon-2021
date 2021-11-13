import json
import math

for city in ['amsterdam', 'brussels', 'paris', 'london', 'berlin']:
    input_file = f'/Users/mhindery/repos/otainsight/hackathon-scrapy/workshop/{city}.json'

    with open(input_file) as f:
        hotels = json.load(f)

    # num hotels and num rooms
    print(city, f'hotels: {len(hotels)}')
    print(city, f"num_rooms: {sum([h['num_rooms'] for h in hotels if h['num_rooms']])}")

    # furthest hotels
    distance_hotels = []
    max_distance = 0
    for idxi, hoteli in enumerate(hotels):
        for idxj, hotelj in enumerate(hotels):
            if idxi == idxj:
                continue
            distance = math.sqrt(
                (abs(hoteli['latitude'] - hotelj['latitude']) * abs(hoteli['latitude'] - hotelj['latitude'])) + (abs(hoteli['longitude'] - hotelj['longitude']) * abs(hoteli['longitude'] - hotelj['longitude']))
                )
            if distance > max_distance:
                max_distance = distance
                distance_hotels = (hoteli['hotel_name'], hotelj['hotel_name'])

    print(city, max_distance, distance_hotels)
    print()
