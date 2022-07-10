from scrapy.item import Item, Field


class HotelItem(Item):
    destination = Field()
    id = Field()
    name = Field()
    rooms = Field()
    address = Field()
    latitude = Field()
    longitude = Field()
    stars = Field()


class RateItem(Item):
    destination = Field()
    hotel_id = Field()
    arrival = Field()
    departure = Field()
    persons = Field()
    room = Field()


class RoomItem(Item):
    name = Field()
    price = Field()
    breakfast = Field()
    refundable = Field()
    max_persons = Field()
