import scrapy
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesSellmaxSpider(car_prices_spider(source='Sellmax')):
    def answers_to_offer_questions(self):
        return {
            # The title is Salvaged or Rebuilt, I don't have a title
            'Tell us about your car title': 'The title is clean',
            # One or multiple tires are flat, One or multiple wheels are removed
            'Are the wheels on the car? And are the tires inflated?': 'All the wheels are mounted and the tires have air',
            # It starts but doesn't drive, It is unable to start
            'Does it drive?': 'The Vehicle starts and drives',
            # Some panels are unattached or missing
            'Any removed/loose exterior body panels?': 'All body panels (hoods,bumpers,doors etc.) are properly in place and attached',
            # It has damage that is larger than a baseball
            'Is the body of the car damaged?': 'It has no damage to the exterior',
            # There is glass, lights, or mirrors missing.
            'Are any mirrors,glass or lights damaged?': 'All glass,lights, and mirrors are intact',
            # Some interior parts are damaged, or removed
            'Have any interior parts been damaged, or taken out?': 'All interior parts like your radio, seats and airbags are properly in place and connected',
            # Yes, it has flood or fire damage.
            'Does the vehicle have any flood or fire damage?': 'The vehicle does not have flood or fire damage.',
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=zip',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
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

        zip_response = yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/google-api.php?action=stateWithZip',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'zip': result['zip_code'],
            },
        )

        zip_data = zip_response.json()

        postal_code = zip_data['postal_code']
        state = zip_data['state']
        city = zip_data['city']

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=what-title',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'postal_code': postal_code,
                'state': state,
                'city': city,
            },
        )

        title = 'clean'
        result['title'] = title.title()

        tires_inflated_step_response = yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=tires-inflated',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'what_title': title,
            },
        )

        tires_inflated_step_data = tires_inflated_step_response.json()

        tires_inflated = 'yes'
        tires_flat_driver_front = tires_inflated_step_data['tires_flat_driver_front']
        tires_flat_driver_rear = tires_inflated_step_data['tires_flat_driver_rear']
        tires_flat_passenger_front = tires_inflated_step_data['tires_flat_passenger_front']
        tires_flat_passenger_rear = tires_inflated_step_data['tires_flat_passenger_rear']

        result['Tires inflated'] = tires_inflated.title()
        result['Front driver side tire flat'] = tires_flat_driver_front.title()
        result['Rear driver side tire flat'] = tires_flat_driver_rear.title()
        result['Front passenger side tire flat'] = tires_flat_passenger_front.title()
        result['Rear passenger side tire flat'] = tires_flat_passenger_rear.title()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=does-it-drive',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'tires_inflated': tires_inflated,
                'tires_flat_driver_front': tires_flat_driver_front,
                'tires_flat_driver_rear': tires_flat_driver_rear,
                'tires_flat_passenger_front': tires_flat_passenger_front,
                'tires_flat_passenger_rear': tires_flat_passenger_rear,
            },
        )

        does_it_drive = 'start_and_drive'
        result['Does it drive'] = does_it_drive.replace('_', ' ').title()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=odometer',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'does_it_drive': 'start_and_drive',
            },
        )

        body_panels_step_response = yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=body-panels',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'odometer': str(result['mileage']),
            },
        )

        body_panels_step_data = body_panels_step_response.json()

        body_panel = 'no'
        body_panels_driver_front = body_panels_step_data['body_panels_driver_front']
        body_panels_driver_rear = body_panels_step_data['body_panels_driver_rear']
        body_panels_passenger_front = body_panels_step_data['body_panels_passenger_front']
        body_panels_passenger_rear = body_panels_step_data['body_panels_passenger_rear']

        result['Does it have damaged body panels?'] = body_panel.title()
        result['Front driver side body panel damaged'] = body_panels_driver_front.title()
        result['Rear driver side body panel damaged'] = body_panels_driver_rear.title()
        result['Front passenger side body panel damaged'] = body_panels_passenger_front.title()
        result['Rear passenger side body panel damaged'] = body_panels_passenger_rear.title()

        body_damage_with_popup_step_response = yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=body-damage-with-popup',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'body_panel': body_panel,
                'body_panels_driver_front': body_panels_driver_front,
                'body_panels_driver_rear': body_panels_driver_rear,
                'body_panels_passenger_front': body_panels_passenger_front,
                'body_panels_passenger_rear': body_panels_passenger_rear,
            },
        )

        body_damage_with_popup_step_data = body_damage_with_popup_step_response.json()

        body_damage = 'no'
        body_damage_driver_front = body_damage_with_popup_step_data[
            'body_damage_driver_front']
        body_damage_driver_rear = body_damage_with_popup_step_data['body_damage_driver_rear']
        body_damage_passenger_front = body_damage_with_popup_step_data[
            'body_damage_passenger_front']
        body_damage_passenger_rear = body_damage_with_popup_step_data[
            'body_damage_passenger_rear']

        result['Does it have a damaged body?'] = body_damage.title()
        result['Front driver side body damaged'] = body_damage_driver_front.title()
        result['Rear driver side body damaged'] = body_damage_driver_rear.title()
        result['Front passenger side body damaged'] = body_damage_passenger_front.title()
        result['Rear passenger side body damaged'] = body_damage_passenger_rear.title()

        glass_mirrors_step_response = yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=glass-mirrors',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'body_damage': body_damage,
                'body_damage_driver_front': body_damage_driver_front,
                'body_damage_driver_rear': body_damage_driver_rear,
                'body_damage_passenger_front': body_damage_passenger_front,
                'body_damage_passenger_rear': body_damage_passenger_rear,
            },
        )

        glass_mirrors_step_data = glass_mirrors_step_response.json()

        glass_mirrors = 'no'
        mirrors_lights_glass_driver_front = glass_mirrors_step_data[
            'mirrors_lights_glass_driver_front']
        mirrors_lights_glass_driver_rear = glass_mirrors_step_data[
            'mirrors_lights_glass_driver_rear']
        mirrors_lights_glass_passenger_front = glass_mirrors_step_data[
            'mirrors_lights_glass_passenger_front']
        mirrors_lights_glass_passenger_rear = glass_mirrors_step_data[
            'mirrors_lights_glass_passenger_rear']

        result['Does it have any damaged mirrors lights glass?'] = glass_mirrors.title()
        result['Front driver side mirrors lights glass damaged'] = mirrors_lights_glass_driver_front.title()
        result['Rear driver side mirrors lights glass damaged'] = mirrors_lights_glass_driver_rear.title()
        result['Front passenger side mirrors lights glass damaged'] = mirrors_lights_glass_passenger_front.title()
        result['Rear passenger side mirrors lights glass damaged'] = mirrors_lights_glass_passenger_rear.title()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=interior-parts',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'glass_mirrors': glass_mirrors,
                'mirrors_lights_glass_driver_front': mirrors_lights_glass_driver_front,
                'mirrors_lights_glass_driver_rear': mirrors_lights_glass_driver_rear,
                'mirrors_lights_glass_passenger_front': mirrors_lights_glass_passenger_front,
                'mirrors_lights_glass_passenger_rear': mirrors_lights_glass_passenger_rear,
            },
        )

        interior_parts = 'no'
        result['Is the interior parts damaged?'] = interior_parts.title()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=flood-fire',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'interior_parts': interior_parts,
            },
        )

        flood_fire = 'no'
        result['Has the car ever been in a flood or fire?'] = flood_fire.title()

        yield scrapy.FormRequest(
            method='POST',
            url='https://sellmax.com/quote/show-quote-form.php?step=submit-form-type-2',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://sellmax.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'flood_fire': flood_fire,
            },
        )

        offer_response = yield scrapy.Request(
            method='GET',
            url='https://sellmax.com/quote/submit-form.php',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://sellmax.com/quote/",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "ci_session=98gltci1b3jm0h2ba5kkboblef",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
        )

        price = float(offer_response.css('#form-starting-point > div > div > div.col-lg-5.vin-pick-john > div.vin-pick > p::text').get(
        ).replace('$', '').replace(',', '').replace(' ', ''))

        result['price'] = price

        yield result
