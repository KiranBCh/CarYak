from datetime import datetime
import scrapy
import scrapy.http
from car_prices.spiders.car_prices import car_prices_spider
from car_prices.exceptions import ProxyBlocked
import random
from uuid import uuid4
import hmac
import hashlib
import json
import time


class CarPricesVroomSpider(car_prices_spider(source='Vroom')):
    captcha_site_key = '6Le6wLMgAAAAALm7gYrofvWVwOPFm2YVO0gTSsdQ'
    datadog_session_duration_milliseconds = 900_000

    def answers_to_offer_questions(self):
        return {
            'How many keys do you have for this vehicle?': '2+',  # 1, 2+
            'Sell or Trade-in?': 'Sell',  # Sell, Trade, Not Sure
            'Has your vehicle been in an accident?': 'NO',  # YES, NO
            # Clean, Lemon, Rebuilt Salvage, True Miles Unknown
            'What type of title does the vehicle have?': 'Clean',
            # LOAN, LEASE, NEITHER
            'Do you currently have a loan or lease on your vehicle?': 'NEITHER',
            'Mechanical & Electrical Issues': 'No Mechanical or Electrical Issues',
            'Exterior Damage': 'No Exterior Damage',
            'Interior Damage': 'No Interior Damage',
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions()

        session_uuid = str(uuid4())
        user_uuid = str(uuid4())
        trcksesh_uuid = str(uuid4())
        datadog_uuid = ''.join((lambda num: f'{(num ^ random.randrange(16) >> num // 4):x}')(int(character))
                               if character in ['0', '1', '8'] else character for character in '10000000-1000-4000-8000-100000000000')
        datadog_creation_milliseconds_since_epoch = time.time_ns() // 1_000_000
        datadog_expiry_milliseconds_since_epoch = datadog_creation_milliseconds_since_epoch + \
            self.datadog_session_duration_milliseconds
        datadog_session = f'rum=1&id={datadog_uuid}&created={datadog_creation_milliseconds_since_epoch}&expire={datadog_expiry_milliseconds_since_epoch}'
        correlation_id = random.randbytes(16).hex()
        google_ads_id_random_part = random.randrange(2**31-1)
        google_ads_id_milliseconds_since_epoch_part = time.time_ns() // 1_000_000

        offer_start_response = yield scrapy.http.JsonRequest(
            url='https://www.vroom.com/sell',
        )

        if offer_start_response.url == 'https://www.vroom.com/non-usa':
            raise ProxyBlocked()

        cat_data_response = yield scrapy.Request(
            url=f'https://www.vroom.com/cat-data/{session_uuid}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.vroom.com/sell",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-9ddcb0d1-d616-422c-b9fc-cf2d850cac99-1679294195; fsid=90df6811-9549-4525-8c8e-876c60bd20a6; first_visit=90df6811-9549-4525-8c8e-876c60bd20a6-602-1679294195; sitePhoneNumber=(855)%20524-1300; ajs_anonymous_id=da259d36-c926-4d68-a0c1-e303f738d089; _gcl_au=1.1.1372976582.1679294292; trcksesh=6ccde688-6853-479e-91ab-397a5153eead; _dd_s=rum=1&id=81ee931b-6ccb-413b-80d5-0d71a1324abe&created=1679300159218&expire=1679301059218; uuid=a4666f9c-4040-440c-bfdb-05b3cee179f7",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            cookies={
                # "rum=1&id=81ee931b-6ccb-413b-80d5-0d71a1324abe&created=1679300159218&expire=1679301075091",
                "_dd_s": datadog_session,
                # "1.1.1372976582.1679294292",
                "_gcl_au": f'1.1.{google_ads_id_random_part}.{google_ads_id_milliseconds_since_epoch_part}',
                "ajs_anonymous_id": user_uuid,
                "trcksesh": trcksesh_uuid,
                "uuid": session_uuid,
            },
        )

        cat_data = cat_data_response.json()

        site_phone_number = cat_data['sitePhoneNumber']
        site_region = cat_data['geo']['region']
        site_city = cat_data['geo']['city']

        build_id_response = yield scrapy.FormRequest(
            method='GET',
            url='https://www.vroom.com/sell/vehicleInformation',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.vroom.com/sell",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-05904598-ccce-48ea-bfff-26326e8b97bb-1679285884; fsid=bc8afa27-ef2c-404e-a97c-3d40573eb0fd; first_visit=bc8afa27-ef2c-404e-a97c-3d40573eb0fd-602-1679285884; _dd_s=rum=1&id=3044acba-b2f2-4ce0-9b5d-e0e2b29432bb&created=1679285886064&expire=1679286810122; uuid=25f23116-0b24-4645-b33f-8eb34d451fbf; sitePhoneNumber=(855)%20524-1300; ajs_anonymous_id=eb0066f3-c577-401f-be64-4a971df84b34; _gcl_au=1.1.184099259.1679285891; trcksesh=2b16f3c2-4563-42df-bd53-0524ab230941",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            cookies={
                "sitePhoneNumber": site_phone_number,
            },
            formdata={
                'vehicle': result['vin_number'],
            },
        )

        build_id = json.loads(build_id_response.xpath(
            '/html/body/script[@id="__NEXT_DATA__"]/text()').get())['buildId']

        vehicle_info_captcha_result = yield from self.solving_recaptchav2_coroutine(
            website_url='https://www.vroom.com/',
            website_key=self.captcha_site_key,
            proxy=result['proxy'],
        )

        vehicle_info_captcha_solution_token = vehicle_info_captcha_result

        vin_decoded_response = yield scrapy.http.JsonRequest(
            url='https://www.vroom.com/appraisal/api/details',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.vroom.com/sell/vehicleInformation?vehicle={result['vin_number']}",
                "Content-Type": "application/json",
                "Origin": "https://www.vroom.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-468e8372-39e6-4f9c-96ce-ef652c037601-1678870030; fsid=8fd70381-0ef1-476c-8260-c31a5ae9d87f; first_visit=8fd70381-0ef1-476c-8260-c31a5ae9d87f-602-1678870030; _dd_s=rum=1&id=bd19e7a2-5bde-496b-b0e3-63d480ea58e0&created=1678870032575&expire=1678871000718; uuid=ec91bbbc-42d7-4afb-8154-6795e8fd71e0; sitePhoneNumber=(855)%20524-1300; ajs_anonymous_id=dbd89955-cc9b-48e8-844a-728875401fca; _gcl_au=1.1.1452996852.1678870038; trcksesh=e0f6e052-6b5d-4bbc-9c6c-64a113ed7444",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "vehicleId": result['vin_number'],
                "token": vehicle_info_captcha_solution_token,
            },
        )

        vehicle_info = vin_decoded_response.json()

        basic_info = vehicle_info['vehicleInfo']
        make = basic_info['make']
        model = basic_info['model']
        year = basic_info['year']
        colour = basic_info['exteriorColor']

        additional_info = vehicle_info['dataProviderInfo']['carstory']
        chosen_features = [info['name']
                           for info in additional_info['features'] if info['selected']]
        style = additional_info['style']

        offer_start_response = yield scrapy.FormRequest(
            method='GET',
            url=f'https://www.vroom.com/appraisal/_next/data/{build_id}/review.json',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.vroom.com/sell/vehicleInformation?vehicle={result['vin_number']}",
                "x-nextjs-data": "1",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-05904598-ccce-48ea-bfff-26326e8b97bb-1679285884; fsid=bc8afa27-ef2c-404e-a97c-3d40573eb0fd; first_visit=bc8afa27-ef2c-404e-a97c-3d40573eb0fd-602-1679285884; _dd_s=rum=1&id=3044acba-b2f2-4ce0-9b5d-e0e2b29432bb&created=1679285886064&expire=1679286923292; uuid=25f23116-0b24-4645-b33f-8eb34d451fbf; sitePhoneNumber=(855)%20524-1300; ajs_anonymous_id=eb0066f3-c577-401f-be64-4a971df84b34; _gcl_au=1.1.184099259.1679285891; trcksesh=2b16f3c2-4563-42df-bd53-0524ab230941",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'vin': result['vin_number'],
            },
        )

        offer_start_info = offer_start_response.json()

        offer_token = offer_start_info['pageProps']['token']

        offer_attribution_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.vroom.com/api/weblead/attribution',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.vroom.com/sell/review?vin={result['vin_number']}",
                "Content-Type": "application/json",
                "Origin": "https://www.vroom.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-c77c14cb-fcc3-472c-85fa-1aae6a0c1796-1678249797; fsid=df49710c-0723-405a-90c2-fc189d39f7c5; first_visit=df49710c-0723-405a-90c2-fc189d39f7c5-512-1678249797; _dd_s=rum=1&id=83ccb516-14aa-47df-8b5d-2a77907caed8&created=1678249798637&expire=1678250973249; uuid=f473ed54-09f2-4105-8000-ab0c62591f8b; sitePhoneNumber=(855)%20524-1300; _gcl_au=1.1.553662791.1678249802; trcksesh=764e26a0-5a41-4e54-994a-d39c4294e4b3",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "type": "Website",
                "tradeIn": False,
                "message": {
                    "form": "appraisal",
                    "brand": "Vroom",
                    "site": "www.vroom.com"
                },
                "person": {
                    "consent": [
                        {
                            "type": "phone",
                            "granted": True
                        },
                        {
                            "type": "TCPA",
                            "granted": True
                        },
                        {
                            "type": "email",
                            "granted": False
                        }
                    ],
                    "state": site_region,
                    "city": site_city,
                    "firstName": result['first_name'],
                    "lastName": result['last_name'],
                    "phone": [
                        {
                            "type": None,
                            "number": result['phone_number']
                        }
                    ],
                    "email": [
                        {
                            "type": None,
                            "address": result['email'],
                        }
                    ],
                    "address": [
                        {}
                    ]
                },
                "weblead": {
                    "webpage": "appraisal",
                    "dealership": "Vroom",
                    "subid": "",
                    "gclid": "",
                    "sessionid": session_uuid,
                    "userid": user_uuid,
                },
                "correlationId": correlation_id,
            },
        )

        offer_submission_captcha_result = yield from self.solving_recaptchav2_coroutine(
            website_url='https://www.vroom.com/',
            website_key=self.captcha_site_key,
            proxy=result['proxy']
        )

        offer_submission_captcha_solution_token = offer_submission_captcha_result

        submission_time = datetime.utcnow().isoformat()[:23] + 'Z'

        offer_data = {
            "payload": {
                "DateSubmitted": submission_time,
                "form": "sell",
                "lead_id": correlation_id,
                "anonymous_id": user_uuid,
                "vin": result['vin_number'],
                "year": result['year'],
                "make": make,
                "model": model,
                "trim": style,
                "mileage": result['mileage'],
                "exteriorColor": "Black",
                "keysAmount": "2+",
                "options": chosen_features,
                "zipCode": result['zip_code'],
                "hasAccident": "No",
                "titleStatus": "Clean",
                "lienType": "none",
                "bankName": "",
                "interiorCondition": "Above Average",
                "seats": "Cloth",
                "smokedIn": "No",
                "exteriorCondition": "Above Average",
                "tiresAndWheels": "Under 5K",
                "hailDamage": "No",
                "afterMarket": [],
                "otherAfterMarket": "",
                "rust": "No",
                "dents": "No",
                "dentsPanels": 0,
                "paintChipping": "No",
                "paintChippingPanels": 0,
                "scratches": "No",
                "mechanicalCondition": "Above Average",
                "runnable": "Yes",
                "warningLights": "No",
                "warningLightsValues": [],
                "otherWarning": "",
                "floodFireDamage": "No",
                "additionalDetails": "suyc-condition-category-questions: true",
                "firstName": result['first_name'],
                "lastName": result['last_name'],
                "email": result['email'],
                "phoneNumber": result['phone_number'],
                "dealership": "vroom",
                "brand": "vroom",
                "type": "website",
                "utm_campaign": "",
                "utm_content": "",
                "utm_medium": "",
                "utm_source": "",
                "utm_term": "",
                "utm_keyword": "",
                "utm_subsource": ""
            },
            "token": offer_submission_captcha_solution_token,
        }

        offer_data_string = json.dumps(offer_data, separators=(',', ':'))

        offer_signature = hmac.new(offer_token.encode(
        ), offer_data_string.encode(), hashlib.sha256).hexdigest()

        offer_response = yield scrapy.Request(
            method='POST',
            url='https://www.vroom.com/appraisal/api/appraisal',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.vroom.com/sell/review?vin={result['vin_number']}",
                "Content-Type": "application/json",
                                "X-Signature": offer_signature,
                                "X-Token": offer_token,
                "Origin": "https://www.vroom.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "fpid=fpid-c77c14cb-fcc3-472c-85fa-1aae6a0c1796-1678249797; fsid=df49710c-0723-405a-90c2-fc189d39f7c5; first_visit=df49710c-0723-405a-90c2-fc189d39f7c5-512-1678249797; _dd_s=rum=1&id=83ccb516-14aa-47df-8b5d-2a77907caed8&created=1678249798637&expire=1678250973249; uuid=f473ed54-09f2-4105-8000-ab0c62591f8b; sitePhoneNumber=(855)%20524-1300; _gcl_au=1.1.553662791.1678249802; trcksesh=764e26a0-5a41-4e54-994a-d39c4294e4b3",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers",
            },
            body=offer_data_string,
        )

        offer = offer_response.json()

        price = float(offer['data']['Price__c'])

        result['price'] = price
        yield result
