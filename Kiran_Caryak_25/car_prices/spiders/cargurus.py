from random import randint
import re
import json
import scrapy
import scrapy.http
import time
from typing import cast
from car_prices.exceptions import CaptchaFailure, CantMakeOfferForVin, OfferAlreadyExists
from car_prices.spiders.car_prices import car_prices_spider
import urllib.parse


class CarPricesCargurusSpider(car_prices_spider(source='Cargurus')):
    site_conditions = {
        'bad': 'Rough',
        'moderate': 'Good',
        'good': 'Amazing',
        'excellent': 'Amazing',
    }
    condition_codes = {
        'bad': 'ROUGH',
        'moderate': 'OKAY',
        'good': 'GREAT',
        'excellent': 'GREAT',
    }

    code_content_pattern = re.compile(r'{.*}')
    datadome_id_pattern = re.compile(r'datadome=(.+?);')

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    def answers_to_offer_questions(self, condition):
        return {
            "Has the vehicle ever been in an accident?": 'None',
            "What is the condition of the vehicle?": self.site_conditions[condition],
            "How are the tires?": 'Good To Go',
            'Any Wheel Damage?': 'No',
            'Does your vehicle have mechanical defects or dashboard warnings?': 'No',
            'Does your vehicle have any issues that would stop us from driving it?': 'No',
            'Does your vehicle have any exterior damage, including hail damage?': 'No',
            'Does the windshield need replacing, have cracks, or have chips larger than a dime?': 'No',
            'Are there any aftermarket parts on the vehicle?': 'No',
            'Has your vehicle ever been smoked in?': 'No',
            'How many keys are there for this vehicle?': '2+',
            "What's the ownership status of your vehicle?": 'Owned',
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions(
            result['condition'])

        random_wait_time = randint(10, 15)

        self.logger.debug(f'Waiting for {random_wait_time} seconds')
        time.sleep(random_wait_time)

        datadome_request = scrapy.http.FormRequest(
            method='GET',
            url='https://www.cargurus.com/sell-car/',
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            formdata={
                "pid": "SellMyCarDesktopHeader"
            },
        )

        offer_url = 'https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader'

        datadome_response = yield datadome_request

        if datadome_response.status >= 400:
            captcha_info_string = datadome_response.xpath('/html/body/script[1]/text()').get()
            captcha_info = json.loads(cast(list[str], self.code_content_pattern.search(captcha_info_string))[0].replace("'", '"'))

            captcha_id = cast(list[str], self.datadome_id_pattern.search(datadome_response.headers.getlist('Set-Cookie')[0].decode()))[1]

            captcha_host = captcha_info['host']
            captcha_initial_id = captcha_info['cid']
            captcha_hash = captcha_info['hsh']
            captcha_t = captcha_info['t']
            captcha_s = captcha_info['s']
            captcha_e = captcha_info['e']

            if captcha_t == 'bv':
                raise CaptchaFailure(f'IP was banned by {offer_url}')

            captcha_referer = urllib.parse.quote(offer_url, safe='')
            captcha_url = f'https://{captcha_host}/captcha/?initialCid={captcha_initial_id}&hash={captcha_hash}&cid={captcha_id}&t={captcha_t}&referer={captcha_referer}&s={captcha_s}&e={captcha_e}'

            datadome_cookie = yield from self.solving_datadome_captcha_coroutine(
                website_url=offer_url,
                captcha_url=captcha_url,
                proxy=result['proxy'],
            )

            datadome_response = yield datadome_request.replace(cookies=datadome_cookie)

            if datadome_response.status >= 400:
                raise CaptchaFailure(f'IP was banned by {offer_url}')

        vin_details_response = yield scrapy.Request(
            method='POST',
            url='https://www.cargurus.com/sell-car/vinValidation.action',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "content-length": "256",
                "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryhBnz1ZiwiccGWnCv",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; datadome=1lb4O~7YbG1kDcNJFeuoU~K4YLZHg-Ifkyy8ldsCes8nwzbaEEMQpWKmCXSPySFSl51~w5Rb~nDmT5ynq9x9Vreha0VVkkoZXRv7qpm76cVb5WByw6~TDFjiW3KMV--y; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2",
                "origin": "https://www.cargurus.com",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            body=f'------WebKitFormBoundaryhBnz1ZiwiccGWnCv\r\nContent-Disposition: form-data; name="vin"\r\n\r\n{result["vin_number"]}\r\n------WebKitFormBoundaryhBnz1ZiwiccGWnCv\r\nContent-Disposition: form-data; name="withCarDetails"\r\n\r\ntrue\r\n------WebKitFormBoundaryhBnz1ZiwiccGWnCv--\r\n',
        )

        vin_details = vin_details_response.json()['data']

        if not vin_details['isValid']:
            raise OfferAlreadyExists()

        year_id = vin_details['carDetails']['year']
        make_id = vin_details['carDetails']['make']
        model_id = vin_details['carDetails']['model']
        # trim_id = vin_details['carDetails']['trim']
        year = vin_details['carDetails']['yearName']
        make = vin_details['carDetails']['makerName']
        model = vin_details['carDetails']['modelName']
        # trim = vin_details['carDetails']['trimName']

        trim_response = yield scrapy.http.FormRequest(
            method='GET',
            url='https://www.cargurus.com/Cars/getSelectedModelCarTrimsAJAX.action',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2; datadome=6a5~mpi35dj4oPiFeXEplQWx8VC-C~A7FhLoVi3Z6bjzj9YiQ3BJMkkkRUexzsxS-HjzSnqzYM7Ndd_9GjlkCSZfx-_vkxi-CNgWBd3Y_gSQROz64dtBYQZamo3kYbGc",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            formdata={
                "showInactive": "false",
                "useInventoryService": "false",
                "localCountryCarsOnly": "true",
                "outputFormat": "REACT",
                "model": model_id
            },
        )

        cars = trim_response.json()['cars']

        trims = {item['id']: item['trims'] for item in cars}[year_id]

        trim_candidates = trims
        trim_candidates.sort(reverse=True, key=lambda trim: self.vehicle_aspect_match_score(
            ' '.join([make, model, trim['name']]), result['kbb_details']['vehicle_name']))

        trim_item = trim_candidates[0]
        #trim = trim_item['name']
        trim_id = trim_item['id']

        transmission_response = yield scrapy.http.FormRequest(
            method='GET',
            url='https://www.cargurus.com/Cars/getTransmissionListTrimFirstJson.action',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2; datadome=6a5~mpi35dj4oPiFeXEplQWx8VC-C~A7FhLoVi3Z6bjzj9YiQ3BJMkkkRUexzsxS-HjzSnqzYM7Ndd_9GjlkCSZfx-_vkxi-CNgWBd3Y_gSQROz64dtBYQZamo3kYbGc",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            formdata={
                "showInactive": "false",
                "useInventoryService": "true",
                "localCountryCarsOnly": "true",
                "outputFormat": "REACT",
                "trim": trim_id,
            },
        )

        transmissions = transmission_response.json()['trimSpecific']['values']
        transmission_candidates = transmissions
        transmission_candidates.sort(reverse=True, key=lambda transmission: self.vehicle_aspect_match_score(
            transmission['name'], result['transmission']))

        transmission_item = transmission_candidates[0]
        #transmission = transmission_item['name']
        transmission_id = transmission_item['id']

        engine_response = yield scrapy.http.FormRequest(
            method='GET',
            url='https://www.cargurus.com/Cars/getEngineList.action',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2; datadome=6a5~mpi35dj4oPiFeXEplQWx8VC-C~A7FhLoVi3Z6bjzj9YiQ3BJMkkkRUexzsxS-HjzSnqzYM7Ndd_9GjlkCSZfx-_vkxi-CNgWBd3Y_gSQROz64dtBYQZamo3kYbGc",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            formdata={
                "showInactive": "false",
                "useInventoryService": "true",
                "localCountryCarsOnly": "true",
                "outputFormat": "REACT",
                "trim": trim_id,
            },
        )

        engine_candidates = engine_response.json()
        engine_candidates.sort(reverse=True, key=lambda engine: self.vehicle_aspect_match_score(
            engine['name'], result['engine']))

        engine_item = engine_candidates[0]
        #engine = engine_item['name']
        engine_id = engine_item['id']

        options_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.cargurus.com/WholesaleOffer/api/wholesaleoffer/v1/cgChromeOptions',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "content-length": "100",
                "content-type": "application/json; charset=utf-8",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2; datadome=5VTCteV5nTks5wKWJWEbjTnRixNxD_fHvMw9zhcFCPR-VG5m-21c8bw2a~nSHYN_vQlJYHFwQUPHHE1uTVmob9qMKLzfCivaJkaw7Yeg0odXtovql-M_LAYMI1QQMFZx; CarGurusDevice=20b789e3-442c-4774-a145-55b78d1f3caa",
                "origin": "https://www.cargurus.com",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            data={
                "engineId": str(engine_id),
                "transmissionId": str(transmission_id),
                "trim": trim_id,
                "vin": result['vin_number'],
                "zip": result['zip_code']
            },
        )

        options_data = options_response.json()['data']

        if options_data == None:
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)

        trim_info = next(
            trim for trim in options_data['vehicle']['trims'] if trim['isSelected'])

        style_id = trim_info['styleId']
        options = trim_info['options']
        colours = trim_info['exteriorColor']
        colour_names = [colour['name'] for colour in colours]
        colour = 'Black' if 'Black' in colour_names else colour_names[0]
        drivetrains = trim_info['driveTrain']
        selected_drivetrains = [
            drivetrain for drivetrain in drivetrains if drivetrain['isSelected']]
        drivetrain_source = selected_drivetrains if len(
            selected_drivetrains) > 0 else drivetrains
        engine_types = trim_info['engine']
        selected_engine_types = [
            engine_type for engine_type in engine_types if engine_type['isSelected']]
        engine_type_source = selected_engine_types if len(
            selected_engine_types) > 0 else engine_types
        transmission_types = trim_info['transmission']
        selected_transmission_types = [
            transmission_type for transmission_type in transmission_types if transmission_type['isSelected']]
        transmission_type_source = selected_transmission_types if len(
            selected_transmission_types) > 0 else transmission_types
        trim_name = trim_info['name']

        drivetrain = drivetrain_source[0]['name']
        drivetrain_id = drivetrain_source[0]['id']
        engine_type = engine_type_source[0]['name']
        engine_type_id = engine_type_source[0]['id']
        engine_cylinder_count = engine_type_source[0]['cylinderCount']
        engine_displacement_in_liters = engine_type_source[0]['displacementInLiters']
        transmission_type = transmission_type_source[0]['name']
        transmission_type_id = transmission_type_source[0]['id']

        site_condition = self.condition_codes[result['condition']]

        offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.cargurus.com/WholesaleOffer/api/wholesaleoffer/v1/offers:evaluate',
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9",
                # "content-length": "2390",
                "content-type": "application/json; charset=utf-8",
                # "cookie": "ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=hqqf-192.46.185.27.1695713614490; InstantOffer=c2d; MultivariateTest=H4sIAAAAAAAAAE1OSQ4CQQj8C2dNaJhmGc9GTYwXnzOZv9uA9niroqhlg%2Bvr9ny877BuwEawgpPCCVg9cRt48T5wI7QgLQkWEQnSSIJYSyKUHk9PS4VCwUuGWVkMByGzKXCi8HbEgc%2F5TdXGHETL2lPhflhVE0fkghHkliOk7j13L8eP9l8Bayzwmmk%2Be4Xnh9TG%2BtC5cuE2wzv%2BhYsn1iyy733fP5bVJ21rAQAADBXiET%2FTIb1ApndtCAutKibvIW81CMm4FBOG7BetuZE%3D; JSESSIONID=3529C360C2AD54D64E61C6FB8556BDAC.10f71; cg-ssid=485d5f9dd409f835dbd7e51f7f8d793b69d6e8a7ff01dcc72848dd6958758561; LSW=www-i-014f12c2b58e99bf2; CarGurusDevice=20b789e3-442c-4774-a145-55b78d1f3caa; datadome=54a3eKUTbGs6LckfQmYse~tZScvEKa6ZmAZ1tPzCpBdFbfBephZj6rL7BohDzpUHWXflDSjf1V_PJJkTCmud1TZheejxpeNii1_vbp9t-hu0gEVTr3JeLumRzIemdQ9n",
                "origin": "https://www.cargurus.com",
                "referer": "https://www.cargurus.com/sell-car/?pid=SellMyCarDesktopHeader",
                "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
            data={
                "cgMakeId": make_id,
                "cgModelId": model_id,
                "cgTransmissionId": str(transmission_id),
                "cgEngineId": str(engine_id),
                "cgOwnershipType": "OWN",
                "cgTrimId": trim_id,
                "cgYearId": year_id,
                "chromeStyleId": style_id,
                "driveTrainId": drivetrain_id,
                "driveTrainName": drivetrain,
                "engineId": engine_type_id,
                "engineName": engine_type,
                "engineCylinderCount": engine_cylinder_count,
                "engineDisplacementInLiters": engine_displacement_in_liters,
                "exteriorColor": colour,
                "licensePlate": "",
                "odometer": result['mileage'],
                "transmissionId": transmission_type_id,
                "transmissionName": transmission_type,
                "vin": result['vin_number'],
                "year": int(year),
                "make": make,
                "model": model,
                "trimName": trim_name,
                "zipCode": result['zip_code'],
                "conditionReport": {
                    "version": "20200825",
                    "categories": [
                        {
                            "category": {
                                "id": "ACCIDENT"
                            },
                            "questions": [
                                {
                                    "id": "ACCIDENT",
                                    "responseOptions": [
                                        {
                                            "id": "0", # "2_PLUS",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "CONDITION"
                            },
                            "questions": [
                                {
                                    "id": "CONDITION",
                                    "responseOptions": [
                                        {
                                            "id": site_condition,
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "TIRE"
                            },
                            "questions": [
                                {
                                    "id": "TIRE_CONDITION",
                                    "responseOptions": [
                                        {
                                            "id": "NO_REPLACEMENT",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                },
                                {
                                    "id": "WHEEL_DAMAGE",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "MECHANICAL"
                            },
                            "questions": [
                                {
                                    "id": "DEFECTS_WARNING",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                },
                                {
                                    "id": "TEST_DRIVE_ISSUES",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "EXTERIOR"
                            },
                            "questions": [
                                {
                                    "id": "EXTERIOR_DAMAGE",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                },
                                {
                                    "id": "WINDSHIELD",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "AFTERMARKET"
                            },
                            "questions": [
                                {
                                    "id": "AFTERMARKET",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "SMOKE"
                            },
                            "questions": [
                                {
                                    "id": "SMOKE",
                                    "responseOptions": [
                                        {
                                            "id": "NO",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        },
                        {
                            "category": {
                                "id": "KEYS"
                            },
                            "questions": [
                                {
                                    "id": "KEYS",
                                    "responseOptions": [
                                        {
                                            "id": "2_PLUS",
                                            "isSelected": True
                                        }
                                    ],
                                    "isAnswered": True
                                }
                            ]
                        }
                    ]
                },
                "userEmail": result['email'],
                "requestSource": "SMC",
                "partnerOfferCallMode": "Default",
                "requestType": "C2D",
                "firstName": "",
                "lastName": "",
                "userPhone": "",
                "pid": "SellMyCarDesktopHeader",
                "options": options
            },
        )

        offer = offer_response.json()['data']

        if offer['isOfferAvailable']:
            result['price'] = float(offer['onlineOffer']['amount'])
        else:
            result['success'] = f'You have no cars for sale'

        yield result
