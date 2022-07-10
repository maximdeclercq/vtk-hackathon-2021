# -*- coding: utf-8 -*-

# Scrapy settings for workshop project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'workshop'
SPIDER_MODULES = ['workshop.spiders']
NEWSPIDER_MODULE = 'workshop.spiders'
DUPEFILTER_DEBUG = False
ITEM_PIPELINES = {'workshop.pipelines.JsonSerializePipeline': 300}

# Optimize speed and reliability
CONCURRENT_ITEMS = 256
CONCURRENT_REQUESTS = 256
CONCURRENT_REQUESTS_PER_DOMAIN = 128
CONCURRENT_REQUESTS_PER_IP = 128
DOWNLOAD_DELAY = 0

# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 30
RETRY_TIMES = 100
RETRY_HTTP_CODES = [429]

# Minimize detectability
COOKIES_ENABLED = True
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}
RANDOMIZE_DOWNLOAD_DELAY = False
ROBOTSTXT_OBEY = False
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
