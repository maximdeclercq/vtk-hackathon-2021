# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from workshop.pubsub import send_message
import json


class WorkshopPipeline(object):
    """ Write each item to pubsub here """

    def process_item(self, item, spider):
        # if spider.name == 'dummy_ota_rates':
        #     send_message(item)

        return item
