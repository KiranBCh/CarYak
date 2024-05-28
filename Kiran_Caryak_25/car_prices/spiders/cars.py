import scrapy
import scrapy.http
from uuid import uuid4
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesCarsSpider(car_prices_spider(source='Cars')):
    accutrade_token = 'e5c6f6ea496ed8afac97830b4601539ab0aa79d1'

    def answers_to_offer_questions(self):
        return {
            'What color is your car? Exterior': 'Black',
            'What color is your car? Interior': 'Black',
            'How many keys do you have?': '2',  # 0, 1, 2, 3+
            'Are you the original owner?': 'Yes',
            'Are you still making payments on your vehicle?': 'No',
            'Was your car ever in an accident?': 'No',
            'Does your vehicle have a clean history report?': 'Yes',
            'Does your vehicle have any current issues?': 'No',
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions()

        visitor_uuid = str(uuid4())

        offer_page_response = yield scrapy.Request(
            method='GET',
            url='https://www.cars.com/sell/instant-offer/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
        )

        vin_decoded_response = yield scrapy.Request(
            method='GET',
            url=f'https://perseus-api-production.accu-trade.com/api/vehicle/by-vin/{result["vin_number"]}/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"Token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
        )

        selected_vehicle = sorted([vehicle for vehicle in vin_decoded_response.json() if vehicle['year'] == result['year']], key=lambda vehicle: self.vehicle_aspect_match_score(
            ' '.join([vehicle['make'], vehicle['model'], vehicle['style']]), result['kbb_details']['vehicle_name']), reverse=True)[0]
        year = selected_vehicle['year']
        make = selected_vehicle['make']
        model = selected_vehicle['model']
        style = selected_vehicle['style']
        selected_gid = selected_vehicle['gid']
        selected_source = selected_vehicle['source']
        vehicle_specialized = selected_vehicle['specialized']

        vehicle_market_details_response = yield scrapy.FormRequest(
            method='GET',
            url=f'https://perseus-api-production.accu-trade.com/api/vehicle/by-guid/{selected_gid}/{result["vin_number"]}/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"Token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'source': str(selected_source),
                'region': result['zip_code'],
            },
        )

        vehicle_market_details = vehicle_market_details_response.json()
        colour_adjustment = next((color['adj'] for color in vehicle_market_details['conditionadj']['colors'] if color['color'] == 'Black'), 0) + next(
            (color['adj'] for color in vehicle_market_details['conditionadj']['int_colors'] if color['color'] == 'Black'), 0)
        vacs = [{
            "ref_id": vac['id'],
            "description": vac['desc'],
            "addded": vac['addded'],
            "amount": vac['amt'],
            "selected": vac['inc'],
            "included": vac['inc']
        } for vac in vehicle_market_details['vacs']]
        vehicle_base_price = vehicle_market_details['vehicleBasePrice']
        vehicle_trade_price = vehicle_market_details['trade']
        vehicle_market_price = vehicle_market_details['market']

        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/stat/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "event": "leadstart",
                "widget_type": "widget"
            },
        )

        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/stat/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "event": "lead_vehicle"
            },
        )

        start_offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/offer/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"Token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "custom_questions": {},
                "vehicle_vin": result['vin_number'],
                "vehicle_year": year,
                "vehicle_make": make,
                "vehicle_model": model,
                "vehicle_style": style,
                "vehicle_source_id": selected_gid,
                "vehicle_specialized": vehicle_specialized,
                "vehicle_mismatch": False,
                "vehicle_manual_entry": False,
                "vehicle_source": selected_source,
                "did_agree_to_tos": False,
                "vacs": vacs,
                "media": {
                    "vehicle": {
                        "other": []
                    }
                },
                "color_adjustment": 0,
                "vehicle_odor_adjustment": 0,
                "completion": 0.33,
                "vehicle_base_price": vehicle_base_price,
                "vehicle_trade_price": vehicle_trade_price,
                "vehicle_market_price": vehicle_market_price,
                "lt": "dealer",
                "visitor_uuid": visitor_uuid,
                "pricing_type": "gp",
                "lead_source": "leadstart_widget",
                "additional_images": [],
                "status": "draft"
            },
        )

        offer_data = start_offer_response.json()
        offer_code = offer_data['code']
        offer_id = offer_data['id']
        offer_extras = offer_data['extras']
        consumer_id = offer_data['consumer']['id']
        offer_range_low = offer_data['range_low']
        offer_range_high = offer_data['range_high']

        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/offer/postal-code-validation/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": "Token e5c6f6ea496ed8afac97830b4601539ab0aa79d1",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "make": make,
                "postal_code": result['zip_code']
            },
        )

        yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "custom_questions": {},
                "vehicle_vin": result['vin_number'],
                "vehicle_year": year,
                "vehicle_make": make,
                "vehicle_model": model,
                "vehicle_style": style,
                "vehicle_source_id": selected_gid,
                "vehicle_specialized": vehicle_specialized,
                "vehicle_mismatch": False,
                "vehicle_source": selected_source,
                "vacs": vacs,
                "vehicle_image": None,
                "color_adjustment": colour_adjustment,
                "id": offer_id,
                "extras": offer_extras,
                "vehicle_mileage": str(result['mileage']),
                "add_optional_photos": False,
                "is_original_owner": True,
                "key_fobs": "2",
                "is_liened": False,
                "vehicle_color": 2,
                "vehicle_interior_color": 2,
                "completion": 0.33,
                "vehicle_base_price": vehicle_base_price,
                "vehicle_trade_price": vehicle_trade_price,
                "vehicle_market_price": vehicle_market_price,
                "lt": "dealer",
                "visitor_uuid": visitor_uuid,
                "pricing_type": "gp",
                "offer_return_link": f"https://cashoffer.accu-trade.com/offer/return/{offer_code}?dlr={self.accutrade_token}",
                "offer_cert_link": f"https://cashoffer.accu-trade.com/offer/cert/{offer_code}?dlr={self.accutrade_token}",
                "new_vehicle_make": None,
                "new_vehicle_model": None,
                "new_vehicle_source": None,
                "new_vehicle_source_id": None,
                "new_vehicle_style": None,
                "new_vehicle_year": None
            },
        )

        yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "custom_questions": {},
                "vehicle_vin": result['vin_number'],
                "vehicle_year": year,
                "vehicle_make": make,
                "vehicle_model": model,
                "vehicle_style": style,
                "vehicle_source_id": selected_gid,
                "vehicle_specialized": vehicle_specialized,
                "vehicle_mismatch": False,
                "vehicle_source": selected_source,
                "vehicle_image": None,
                "media": {
                    "vehicle": {
                        "other": [],
                        "front": None,
                        "front_left_corner": None,
                        "front_right_corner": None,
                        "front_left_tire": None,
                        "front_right_tire": None,
                        "rear": None,
                        "rear_left_corner": None,
                        "rear_right_corner": None,
                        "rear_left_tire": None,
                        "rear_right_tire": None,
                        "left_side": None,
                        "right_side": None,
                        "roof": None,
                        "dashboard": None,
                        "odometer": None,
                        "driver_seat": None,
                        "rear_seat": None
                    },
                    "service_records": [],
                    "modifications": [],
                    "accident": []
                },
                "id": offer_id,
                "extras": offer_extras,
                "vehicle_mileage": str(result['mileage']),
                "add_optional_photos": False,
                "key_fobs": "2",
                "vehicle_color": 2,
                "vehicle_interior_color": 2,
                "has_mechanical_issues": False,
                "has_warning_lights": False,
                "has_modifications": False,
                "has_other_issues": False,
                "has_accident": False,
                "carfax_has_bad_vhr": False,
                "has_significant_issues": False,
                "completion": 0.66,
                "vehicle_base_price": vehicle_base_price,
                "vehicle_trade_price": vehicle_trade_price,
                "vehicle_market_price": vehicle_market_price,
                "pricing_type": "gp",
                "offer_return_link": f"https://cashoffer.accu-trade.com/offer/return/{offer_code}?dlr={self.accutrade_token}",
                "offer_cert_link": f"https://cashoffer.accu-trade.com/offer/cert/{offer_code}?dlr={self.accutrade_token}",
                "mechanical_other_note": ""
            },
        )

        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/stat/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "event": "lead_prepii"
            },
        )

        yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/consumer/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "first_name": result['first_name'],
                "last_name": result['last_name'],
                "cell_phone": result['phone_number'],
                "member_identifier": None,
                "bypass_validation": False,
                "email": result['email'],
                "postal_code": result['zip_code'],
                "id": consumer_id,
                "best_time_to_contact": "1"
            },
        )

        yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "custom_questions": {},
                "vehicle_vin": result['vin_number'],
                "vehicle_year": year,
                "vehicle_make": make,
                "vehicle_model": model,
                "vehicle_style": style,
                "vehicle_source_id": selected_gid,
                "vehicle_specialized": vehicle_specialized,
                "vehicle_mismatch": False,
                "vehicle_source": selected_source,
                "did_agree_to_tos": True,
                "vehicle_image": None,
                "id": offer_id,
                "extras": offer_extras,
                "vehicle_mileage": str(result['mileage']),
                "add_optional_photos": False,
                "key_fobs": "2",
                "vehicle_color": 2,
                "vehicle_interior_color": 2,
                "expect_transact_months": "100",
                "completion": 1,
                "vehicle_base_price": vehicle_base_price,
                "vehicle_trade_price": vehicle_trade_price,
                "vehicle_market_price": vehicle_market_price,
                "pricing_type": "gp",
                "offer_return_link": f"https://cashoffer.accu-trade.com/offer/return/{offer_code}?dlr={self.accutrade_token}",
                "offer_cert_link": f"https://cashoffer.accu-trade.com/offer/cert/{offer_code}?dlr={self.accutrade_token}",
                "offer_view_url": f"https://cashoffer.accu-trade.com/offer/cert/{offer_code}"
            },
        )

        yield scrapy.http.JsonRequest(
            method='POST',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/consumer/send_verification_code/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "mode": "sms"
            },
        )

        # verification_code = input("SMS verification code: ")
        verification_code = 0000

        yield scrapy.http.JsonRequest(
            method='POST',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/consumer/check_verification_code/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": "Token e5c6f6ea496ed8afac97830b4601539ab0aa79d1",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "code": verification_code
            },
        )

        yield scrapy.Request(
            method='POST',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/process/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Content-Length": "0",
                "TE": "trailers"
            },
        )

        yield scrapy.Request(
            method='GET',
            url=f'https://perseus-api-production.accu-trade.com/api/offer/{offer_code}/results/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
        )

        offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://perseus-api-production.accu-trade.com/api/offer/guaranteed-price/calculate/1/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cashoffer.accu-trade.com/",
                "Authorization": f"Token {self.accutrade_token}",
                "PerseusFrontEnd": "consumer-ui",
                "Content-Type": "application/json",
                "Origin": "https://cashoffer.accu-trade.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "consumer": consumer_id,
                "custom_questions": {},
                "vehicle_vin": result['vin_number'],
                "vehicle_year": year,
                "vehicle_make": make,
                "vehicle_model": model,
                "vehicle_style": style,
                "vehicle_source_id": selected_gid,
                "vehicle_specialized": vehicle_specialized,
                "vehicle_mismatch": False,
                "vehicle_manual_entry": False,
                "vehicle_source": selected_source,
                "did_agree_to_tos": True,
                "vacs": vacs,
                "media": {
                    "vehicle": {
                        "other": [],
                        "front": None,
                        "front_left_corner": None,
                        "front_right_corner": None,
                        "front_left_tire": None,
                        "front_right_tire": None,
                        "rear": None,
                        "rear_left_corner": None,
                        "rear_right_corner": None,
                        "rear_left_tire": None,
                        "rear_right_tire": None,
                        "left_side": None,
                        "right_side": None,
                        "roof": None,
                        "dashboard": None,
                        "odometer": None,
                        "driver_seat": None,
                        "rear_seat": None
                    },
                    "service_records": [],
                    "modifications": [],
                    "accident": []
                },
                "color_adjustment": colour_adjustment,
                "vehicle_odor_adjustment": 0,
                "vehicle_image": None,
                "id": offer_id,
                "range_low": offer_range_low,
                "range_high": offer_range_high,
                "needs_dealer_review": False,
                "loan_payoff": None,
                "loan_equity": None,
                "extras": offer_extras,
                "vehicle_mileage": str(result['mileage']),
                "add_optional_photos": False,
                "is_original_owner": True,
                "key_fobs": "2",
                "is_liened": False,
                "vehicle_color": 2,
                "vehicle_interior_color": 2,
                "has_mechanical_issues": False,
                "has_warning_lights": False,
                "has_modifications": False,
                "has_other_issues": False,
                "hasSignificantIssuesRequired": "",
                "has_accident": False,
                "carfax_has_bad_vhr": False,
                "has_significant_issues": False,
                "expect_transact_months": "100",
                "completion": 1,
                "vehicle_base_price": vehicle_base_price,
                "vehicle_trade_price": vehicle_trade_price,
                "vehicle_market_price": vehicle_market_price,
                "lt": "dealer",
                "visitor_uuid": visitor_uuid,
                "pricing_type": "gp",
                "offer_return_link": f"https://cashoffer.accu-trade.com/offer/return/{offer_code}?dlr={self.accutrade_token}",
                "offer_cert_link": f"https://cashoffer.accu-trade.com/offer/cert/{offer_code}?dlr={self.accutrade_token}",
                "lead_source": "leadstart_widget",
                "mechanical_other_note": ""
            },
        )

        result["price"] = float(offer_response.json()['value'])

        yield result
