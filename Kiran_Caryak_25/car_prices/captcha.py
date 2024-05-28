from typing import Generator, cast
import scrapy
import re
import scrapy.http
import time
from car_prices.exceptions import CaptchaFailure


class CaptchaSolver:
    def solving_recaptchav2_coroutine(self, user_agent: str, website_url: str, website_key: str, capsolver_key: str, proxy: str) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
        request = scrapy.http.JsonRequest(
            url='https://api.capsolver.com/createTask',
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/json',
            },
            data={
                'clientKey': capsolver_key,
                'task': {
                    'type': 'ReCaptchaV2Task',
                    'websiteURL': website_url,
                    'websiteKey': website_key,
                    'proxy': proxy,
                    'userAgent': user_agent,
                },
            },
        )

        return (yield from self.solving_captcha_coroutine(
            request=request,
            capsolver_key=capsolver_key,
        ))['gRecaptchaResponse']

    def solving_datadome_captcha_coroutine(
        self,
        user_agent: str,
        capsolver_key: str,
        website_url: str,
        captcha_url: str,
        proxy: str,
    ) -> Generator[scrapy.Request, scrapy.http.TextResponse, dict[str, str]]:
        request = scrapy.http.JsonRequest(
            url='https://api.capsolver.com/createTask',
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/json',
            },
            data={
                'clientKey': capsolver_key,
                'task': {
                    'type': 'DatadomeSliderTask',
                    'websiteURL': website_url,
                    'captchaUrl': captcha_url,
                    "proxy": proxy,
                    "userAgent": user_agent,
                },
            },
        )

        cookie_string = (yield from self.solving_captcha_coroutine(
            request=request,
            capsolver_key=capsolver_key,
        ))['cookie']

        datadome_value = cast(list[str], re.compile(r'datadome=(.+?);').search(cookie_string))[1]

        return {'datadome': datadome_value}

    def solving_captcha_coroutine(self, request: scrapy.Request, capsolver_key: str) -> Generator[scrapy.Request, scrapy.http.TextResponse, dict]:
        captcha_solving_task_creation_response = yield request
        captcha_solving_task_creation = cast(dict, captcha_solving_task_creation_response.json())

        if captcha_solving_task_creation['errorId'] > 0:
            raise CaptchaFailure(
                captcha_solving_task_creation['errorDescription'])

        captcha_solving_task_id = captcha_solving_task_creation['taskId']

        while (True):
            time.sleep(3)
            captcha_solving_task_status_response = yield scrapy.http.JsonRequest(
                url='https://api.capsolver.com/getTaskResult',
                headers={
                    'Accept': '*/*',
                    'Content-Type': 'application/json',
                },
                data={
                    'clientKey': capsolver_key,
                    'taskId': captcha_solving_task_id,
                },
                dont_filter=True,
            )

            captcha_solving_task_status = cast(dict, captcha_solving_task_status_response.json())

            if captcha_solving_task_status['errorId'] > 0:
                raise CaptchaFailure(
                    captcha_solving_task_status['errorDescription'])

            if captcha_solving_task_status['status'] == 'ready':
                return captcha_solving_task_status['solution']
