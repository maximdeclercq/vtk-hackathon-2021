# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import base64
import random
import time

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

server_location = 'http://35.233.25.116'

server_location = 'http://localhost:8282'



class UserAgentDownloaderMiddleware:
    user_agent_choices = [
        "Edg/93", "Edg/94", "Edg/95", "Edg/96",
        "Chrome/93", "Chrome/94", "Chrome/95", "Chrome/96",
        "Firefox/93", "Firefox/94", "Firefox/95", "Firefox/96",
        "Safari/603", "Safari/604", "Safari/605", "Safari/606",
        "Trident/7",
    ]

    def process_request(self, request, spider):
        # user_agent = request.headers.get('User-Agent')
        # Look at what user_agent is by default ...

        # Replace by a random choice from a good list
        request.headers['User-Agent'] = random.choice(self.user_agent_choices)

        return None


class RateLimitRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(2)
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response


class ControlIDCookiesMiddleware:
    def process_request(self, request, spider):
        if '/Berlin' in request.url:
            path = request.url.removeprefix(server_location)
            encoded_path = base64.b64encode(path.encode()).decode('utf-8')
            request.cookies['controlid'] = encoded_path
        return None
