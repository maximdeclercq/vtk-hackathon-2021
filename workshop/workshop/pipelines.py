# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json

from workshop.pubsub import send_hotels_message, send_rates_message


class WorkshopPipeline(object):
    """ Write each item to pubsub here """

    def process_item(self, item, spider):
        if spider.name == 'ota_rates':
            send_rates_message(item)
        elif spider.name == 'ota_hotels':
            send_hotels_message(item)

        return item
