import json
from collections import defaultdict

from itemadapter import ItemAdapter

from workshop.items import HotelItem, RateItem


class JsonSerializePipeline:
    def open_spider(self, spider):
        self.hotels = defaultdict(list)
        self.rates = defaultdict(list)

    def close_spider(self, spider):
        for k, v in self.hotels.items():
            with open(f"hotels-{k.lower()}.json", "w") as f:
                f.write(json.dumps(v, indent=2))
        for k, v in self.rates.items():
            with open(f"rates-{k.lower()}.json", "w") as f:
                f.write(json.dumps(v, indent=2))

    def process_item(self, item, spider):
        if isinstance(item, HotelItem):
            d = ItemAdapter(item).asdict()
            del d["destination"]
            self.hotels[item["destination"]].append(d)
        if isinstance(item, RateItem):
            d = ItemAdapter(item).asdict()
            del d["destination"]
            self.rates[item["destination"]].append(d)
        return item
