# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from logging import Logger, LoggerAdapter
from scrapy import Spider, signals, Request
from scrapy.crawler import Crawler
from scrapy.http import Response, TextResponse, Headers
import textwrap
import json
from json import JSONDecodeError
from typing import cast, Any

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CarPricesSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


def decode(object: Any):
    try:
        return object.decode()

    except (UnicodeDecodeError, AttributeError):
        return str(object)


def format_request_body(body: Any):
    text_body = decode(body)
    try:
        return json.dumps(json.loads(text_body), indent=4)

    except JSONDecodeError:
        return text_body


def decode_headers(headers: Headers):
    entries = (entry.decode() for entry in headers)
    return [{entry: [decode(value) for value in headers.getlist(entry)]} for entry in entries]


def format_headers(headers: Headers):
    return json.dumps(decode_headers(headers), indent=4)


def format_text_response_body(response: TextResponse):
    try:
        return json.dumps(response.json(), indent=4)

    except JSONDecodeError:
        return response.text


def format_response_body(response: Response):
    return format_text_response_body(cast(TextResponse, response)) if hasattr(response, 'json') and hasattr(response, 'text') else str(response.body)


def align_text(text: str, indent_size: int):
    return text.replace('\n', '\n' + ' ' * indent_size)


class CarPricesDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request: Request, spider: Spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request: Request, response: Response, spider: Spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RequestLogger:
    def log_request(self, request: Request, logger: LoggerAdapter) -> None:
        indent_size = 20

        formatted_headers = align_text(format_headers(request.headers), indent_size)
        formatted_body = align_text(format_request_body(request.body), indent_size)

        logger.debug(textwrap.dedent(
            f'''\
                Dispatching request:
                    Method: {request.method}
                    Url: {request.url}
                    Headers: {formatted_headers}
                    Body: {formatted_body}
                '''
        ))

    def process_request(self, request: Request, spider: Spider):
        self.log_request(request, spider.logger)

        return None


class ResponseLogger:
    def log_response(self, response: Response, logger: LoggerAdapter) -> None:
        indent_size = 20

        formatted_headers = align_text(format_headers(response.headers), indent_size)
        formatted_body = align_text(format_response_body(response), indent_size)

        logger.debug(textwrap.dedent(
            f'''\
                Processing HTTP response:
                    Status: {response.status}
                    Url: {response.url}
                    Headers: {formatted_headers}
                    Body: {formatted_body}
                '''
        ))

    def process_response(self, request: Request, response: Response, spider: Spider):
        self.log_response(response, spider.logger)

        return response
