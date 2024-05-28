import scrapy
import scrapy.http
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesShiftSpider(car_prices_spider(source='Shift')):
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    def process_requests(self, result):
        '''
        #We need to solve the captcha first
        shift_homepage_response = yield scrapy.Request(url='https://shift.com/', callback=self.parse_response)

        captcha_info_string = shift_homepage_response.xpath('/html/body/script[1]/text()').get()
        captcha_info = json.loads(re.compile(r'{.*}').search(captcha_info_string)[0].replace("'", '"'))

        captcha_id = re.compile(r'datadome=(.+);').search(shift_homepage_response.headers.getlist('Set-Cookie')[0].decode())[1]

        captcha_host = captcha_info['host']
        captcha_initial_id = captcha_info['cid']
        captcha_hash = captcha_info['hsh']
        captcha_t = captcha_info['t']
        captcha_s = captcha_info['s']
        captcha_e = captcha_info['e']

        captcha_result = yield from self.solving_datadome_captcha_coroutine(
            website_url=f'https://shift.com/',
            captcha_host=captcha_host,
            captcha_id=captcha_id,
            captcha_initial_id=captcha_initial_id,
            captcha_hash=captcha_hash,
            captcha_t=captcha_t,
            captcha_s=captcha_s,
            captcha_e=captcha_e,
            proxy=result['proxy'],
        )

        captcha_solution_cookie = captcha_result.value

        cookie_entries = captcha_solution_cookie.split('; ')

        def cookie_entry_to_key_value_pair(entry):
            pair = entry.split('=')
            return pair if len(pair) == 2 else [pair[0], '']

        cookie_dict = {key: value for key, value in (cookie_entry_to_key_value_pair(entry) for entry in cookie_entries)}

        self.logger.debug(cookie_dict)
        '''

        vin_request = scrapy.http.JsonRequest(
            url=f'https://shift.com/api/consumer/v1/lp_vin_details?vin={result["vin_number"]}',
            method='GET',
            headers={
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'text/json',
            },
            # cookies=[cookie_dict],
            callback=self.parse_json_response,
        )

        vin_decoded_response = yield vin_request

        offer_data = {
            "analytics_info": {
                "context": {
                    "campaign": {
                        "content": '',
                        "medium": '',
                        "name": '',
                        "source": '',
                        "term": '',
                    },
                    "page": {
                        "path": "/sell-my-car/estimate/pet1.ck1pt.Yo83Krrtc4rT_tb5t60HCk3L44P-FawxyEIO_yYlzO7e3XEv7LlJZu4RICc-0LEp04qJ28zgMJ74rN3RZWLwLheEJSPlcj8cMclf3EiZm38Ljpqq_FcHWoAdcp_sKN7p8ymy-qdY-rhiMzutRaxgl0k9..1",
                        "referrer": f"https://shift.com/quote-flow/condition?vin={result['vin_number']}",
                        "search": "",
                        "title": "Dashboard | Shift",
                        "url": "https://shift.com/sell-my-car/estimate/pet1.ck1pt.Yo83Krrtc4rT_tb5t60HCk3L44P-FawxyEIO_yYlzO7e3XEv7LlJZu4RICc-0LEp04qJ28zgMJ74rN3RZWLwLheEJSPlcj8cMclf3EiZm38Ljpqq_FcHWoAdcp_sKN7p8ymy-qdY-rhiMzutRaxgl0k9..1",
                    },
                },
                "google_click_identifier": '',
            },
            "app_info": {
                "app_identifier": "ConsumerWeb",
                "app_version": "1.0.2",
                "build": "2023-02-23T00:32:35Z_bk-gae-29879",
            },
            "auth_info": {
                "csrf_token": "",
                "user_account_csrf_token": "",
            },
            "client_info": {
                "locale": "en-US",
                "os_name": "Win32",
                "os_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "timestamp": "2023-02-23T04:24:40.758Z",
            },
            "request": {
                "token": "pet1.ck1pt.Yo83Krrtc4rT_tb5t60HCk3L44P-FawxyEIO_yYlzO7e3XEv7LlJZu4RICc-0LEp04qJ28zgMJ74rN3RZWLwLheEJSPlcj8cMclf3EiZm38Ljpqq_FcHWoAdcp_sKN7p8ymy-qdY-rhiMzutRaxgl0k9..1",
            },
            "request_id": "itst3JssNoc",
        }

        offer_response = yield scrapy.http.JsonRequest(
            url=f'https://shift.com/clientapi/consumer/seller/get_price_info_by_pricing_event_token_2',
            method='POST',
            headers={
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/json; charset=UTF-8',
            },
            data=offer_data,
            callback=self.parse_json_response,
        )

        instant_cash = offer_response["result"]["content"]["details"]["quote"]["instant_cash"]
        vehicle_details = offer_response["result"]["content"]["details"]["vehicle_details"]
        car_details = offer_response["result"]["content"]["details"]["deal"]["car"]

        result["Does your car have any issues that prevent it from starting or driving?"] = "No"
        result["Does your car have any mechanical issues or persistent dashboard warning lights?"] = "No"
        result["Does your car have any aftermarket modifications?"] = "No"
        result[" Does your car have any persistent odors?"] = "No"
        result["Do you have a loan or lease on this vehicle?"] = "No"
        result["Do any of your vehicle’s exterior panels have damage?"] = "No"
        result["Has your vehicle been in an accident?"] = "No"
        result["Does your vehicle have hail damage (or multiple ding/dents on horizontal panels)"] = "No"
        result["Do any of your interior panels have significant damage or missing parts"] = "No"
        result["Does the vehicle have front and back plates?"] = "Yes"
        result["price"] = float(instant_cash["rounded_amount_usd"])

        yield result
