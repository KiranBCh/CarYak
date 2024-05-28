import scrapy
import scrapy.http
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesCarmaxSpider(car_prices_spider(source='Carmax')):
    site_conditions = {
        'bad': 'Fair',
        'moderate': 'Good',
        'good': 'Very good',
        'excellent': 'Excellent',
    }

    default_kr_key = '121b564c-e39e-43d9-a6ef-d9a1d834952c'

    def answers_to_offer_questions(self, condition):
        return {
            'What is the overall condition of your vehicle?': self.site_conditions[condition],
            'Has the vehicle ever been in an accident?': 'No', # No, Yes
            'Does the vehicle have any frame damage?': 'No', # No, Yes
            'Does the vehicle have any flood damage?': 'No', # No, Yes
            'Has this vehicle been smoked in?': 'No', # No, Yes
            'Are there any mechanical issues or warning lights displayed on the dashboard?': 'No', # No, Yes
            'Has the odometer ever been broken or replaced?': 'No', # No, Yes
            'Are there any panels in need of paint or body work?': 'No', # No, Yes, 1, Yes, 2, Yes, 3+
            'Any major rust and/or hail damage?': 'No', # No, Yes
            'Are any interior parts broken or inoperable?': 'No', # No, Yes, 1, Yes, 2, Yes, 3+
            'Are there any rips, tears, or stains in the interior?': 'No', # No, Yes, 1, Yes, 2, Yes, 3+
            'Do any tires need to be replaced?': 'No', # No, Yes, 1 or 2, Yes, 3 or 4
            'How many keys do you have?': 'No', # 2 or more, 1
            'Does the vehicle have any aftermarket modifications?': 'No', # No, Yes
            'Are there any other issues with the vehicle?': 'No', # No, Yes
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions(result['condition'])

        # Setting the cookies
        yield scrapy.Request(
            method='GET',
            url='https://www.carmax.com/sell-my-car',
            headers={
                "authority": "www.carmax.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-GB,en;q=0.9",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        kr_response = yield scrapy.Request(
            method='GET',
            url='https://www.carmax.com/shared/appraisals/main.bundle.js',
            headers={
                "authority": "www.carmax.com",
                "accept": "*/*",
                "accept-language": "en-GB,en;q=0.9",
                # "cookie": "AKA_A2=A; bm_sz=E86F4F259FE281423162CFE939641F34~YAAQSWjcF6cFhIyIAQAAuRqxlBTO8PKjX5GZqOSBamsTydDYOvlnkTWrlU3XgCZhIZYCw4ktpEZ2/fnlqlMTEoKp+P8uY+z9iRbDyLrnruOuu5x5PI3AjBu9RiU/N5mMn5nhfa+8VDPyHSDzo/8hhAaFJgCGVBLhnjBYOaS5rrIAHgz3XmEJ7JLQFLoifozNcDofHMYXA3usTdfVcbRiTSsJ9YSSmmENrpYn5Aacp3a4pCQ7JZahWk+EDdYapGN/1H6cdSe6wZ3yhLuxgIcSke824FjrEkn137lchgidZ2sqgaU=~3355957~4538694; _abck=CE99441692953F63D3FB8015D5C365C7~0~YAAQSWjcF6IGhIyIAQAA9iGxlAqSF4Kjiobu4xRke7lFLPk+RsE1oGZCmmIskx53zXmdlDzMxkIbgGwbQ7bmQugATbz0zXphaJuQ6g+jSHk2D+7iYHCkjCfzfn6Q08Fz8d5ir7olbl9fTEJLaKfSnkFd0fdI1fvzUloL5jDiIrvLj9uq90S0q+otZK/mLf2kcGg+nWhQt5Fots4mori4edQzd4T6Yd+gfEfWPz6BYvEshWDXsRvSslQsx7biSroxYfKbSOlsMgroGmKYPCYIEvTckqkoHPm0tgK/aYNwB7186fB1BzRLDXN6EaxnSOC/k49NR5Ap18LyIBqRg5lA1WLLWTBrqqR74XZgh57LebQ4IYi7Y46idZixOX96OF7XqSDsyT8QV1VodrFSGSdjSA6SEW6+4I+s~-1~||1-ynaGAUMhIp-1-10-1000-2||~1686125398; ai_user=q3HKJessyuXD7MF/DDPZGI|2023-06-07T07:10:17.104Z; ak_bmsc=F56CC939FD819837F27E595B7F3923BB~000000000000000000000000000000~YAAQSWjcFw0HhIyIAQAAICWxlBRrgArvtIsB4HWuVBwercc1lT1pshUjoFVDNnVJT82J2akiWtfrtx08+WPp8Jz0xmuXrQueogP2M9kVjRlRnEQLzKyMX04OTCMl8rg8jIJ7Rn7b+YAm+kukvBHK64y1GHD5b0Jz5oSboFjkUqgf5liZORhNsITxUwe3qcsI6CuHCCQRHbrZoe3b7ZUKgtPB48PVBYxjDWdE/ykpT/4BhbuefkRtInoxZuVr/44iCpw3zg5nDPJTLhF9Zhp+GefouGBJUr2q/yYmGDC3EkG6xaSJUrZgzHDVQMLQFe1cl0etJ28/RrgH+7viqHvvfaaqSZCE946gw5W2U1B7zNWY6EvwqnAOTJ3nVim+DFMR5pHE3jOBva/qwSsg0JoyIc5UxRBHX+k2yvv7ShifXj7GgxXNU8D5/uvxnc87voxJmFrZLSfJ+vknk+FZXR7rY9ONC6J6wcWNEXO1B6eNlN8iJGJ+AMc7QpU=; bm_sv=85878EE4F7CD0CCE62B7F1898B12207F~YAAQSWjcFxwHhIyIAQAAfSWxlBS9nGZ4jVnby+wEOyP53jRxA/PnGVgdq8eSyBPtY4yoiXvi8qpAX/hEnNrzGDPzwRkjKzq/Bf87NxYUe+kQNZ6q70bK3LObNGNe2STa5OGsnRjw+WfC26X7wXx7WWA+eApzRTk30mgk+T733x4x3gJEoy1AakefHg+CbliRcW6Ejd4Eg/NAMo19K5SYa/TyVrY0QNqDx35u2y5dLEMLhMqFsuevFHi6mvl0eGtY~1; ai_session=jF0TV/h5xr0H330uxXEbol|1686121817771|1686121817771",
                "referer": "https://www.carmax.com/sell-my-car",
                "sec-fetch-dest": "script",
                "sec-fetch-mode": "no-cors",
                "sec-fetch-site": "same-origin",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        kr_key = kr_response.selector.re_first(r'KR:\s*?"(.*?)"') or self.default_kr_key

        token_response = yield scrapy.Request(
            method='GET',
            url='https://www.carmax.com/sell-my-car/api/instant-offer/token',
            headers={
                "authority": "www.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                # "cookie": "AKA_A2=A; bm_sz=E86F4F259FE281423162CFE939641F34~YAAQSWjcF6cFhIyIAQAAuRqxlBTO8PKjX5GZqOSBamsTydDYOvlnkTWrlU3XgCZhIZYCw4ktpEZ2/fnlqlMTEoKp+P8uY+z9iRbDyLrnruOuu5x5PI3AjBu9RiU/N5mMn5nhfa+8VDPyHSDzo/8hhAaFJgCGVBLhnjBYOaS5rrIAHgz3XmEJ7JLQFLoifozNcDofHMYXA3usTdfVcbRiTSsJ9YSSmmENrpYn5Aacp3a4pCQ7JZahWk+EDdYapGN/1H6cdSe6wZ3yhLuxgIcSke824FjrEkn137lchgidZ2sqgaU=~3355957~4538694; _abck=CE99441692953F63D3FB8015D5C365C7~0~YAAQSWjcF6IGhIyIAQAA9iGxlAqSF4Kjiobu4xRke7lFLPk+RsE1oGZCmmIskx53zXmdlDzMxkIbgGwbQ7bmQugATbz0zXphaJuQ6g+jSHk2D+7iYHCkjCfzfn6Q08Fz8d5ir7olbl9fTEJLaKfSnkFd0fdI1fvzUloL5jDiIrvLj9uq90S0q+otZK/mLf2kcGg+nWhQt5Fots4mori4edQzd4T6Yd+gfEfWPz6BYvEshWDXsRvSslQsx7biSroxYfKbSOlsMgroGmKYPCYIEvTckqkoHPm0tgK/aYNwB7186fB1BzRLDXN6EaxnSOC/k49NR5Ap18LyIBqRg5lA1WLLWTBrqqR74XZgh57LebQ4IYi7Y46idZixOX96OF7XqSDsyT8QV1VodrFSGSdjSA6SEW6+4I+s~-1~||1-ynaGAUMhIp-1-10-1000-2||~1686125398; ai_user=q3HKJessyuXD7MF/DDPZGI|2023-06-07T07:10:17.104Z; ak_bmsc=F56CC939FD819837F27E595B7F3923BB~000000000000000000000000000000~YAAQSWjcFw0HhIyIAQAAICWxlBRrgArvtIsB4HWuVBwercc1lT1pshUjoFVDNnVJT82J2akiWtfrtx08+WPp8Jz0xmuXrQueogP2M9kVjRlRnEQLzKyMX04OTCMl8rg8jIJ7Rn7b+YAm+kukvBHK64y1GHD5b0Jz5oSboFjkUqgf5liZORhNsITxUwe3qcsI6CuHCCQRHbrZoe3b7ZUKgtPB48PVBYxjDWdE/ykpT/4BhbuefkRtInoxZuVr/44iCpw3zg5nDPJTLhF9Zhp+GefouGBJUr2q/yYmGDC3EkG6xaSJUrZgzHDVQMLQFe1cl0etJ28/RrgH+7viqHvvfaaqSZCE946gw5W2U1B7zNWY6EvwqnAOTJ3nVim+DFMR5pHE3jOBva/qwSsg0JoyIc5UxRBHX+k2yvv7ShifXj7GgxXNU8D5/uvxnc87voxJmFrZLSfJ+vknk+FZXR7rY9ONC6J6wcWNEXO1B6eNlN8iJGJ+AMc7QpU=; bm_sv=85878EE4F7CD0CCE62B7F1898B12207F~YAAQSWjcFxwHhIyIAQAAfSWxlBS9nGZ4jVnby+wEOyP53jRxA/PnGVgdq8eSyBPtY4yoiXvi8qpAX/hEnNrzGDPzwRkjKzq/Bf87NxYUe+kQNZ6q70bK3LObNGNe2STa5OGsnRjw+WfC26X7wXx7WWA+eApzRTk30mgk+T733x4x3gJEoy1AakefHg+CbliRcW6Ejd4Eg/NAMo19K5SYa/TyVrY0QNqDx35u2y5dLEMLhMqFsuevFHi6mvl0eGtY~1; ai_session=jF0TV/h5xr0H330uxXEbol|1686121817771|1686121817771",
                "referer": "https://www.carmax.com/sell-my-car",
                # "request-id": "|adf6acdd71a7475f81d21b0ab0ec25d7.516ec54133a94d7f",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "suyc_features": "condition-question-email",
                # "traceparent": "00-adf6acdd71a7475f81d21b0ab0ec25d7-516ec54133a94d7f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        token = token_response.json()['token']
        authorization = f'Bearer {token}'

        offer_features_response = yield scrapy.Request(
            method='GET',
            url='https://instant-offers.services.carmax.com/system/features',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        offer_features = offer_features_response.json()

        vin_decoded_response = yield scrapy.FormRequest(
            method='GET',
            url='https://instant-offers.services.carmax.com/profile/vin',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
            formdata={
                'vin': result['vin_number'],
            },
        )

        possible_vehicles = [vehicle for vehicle in vin_decoded_response.json(
        )['matches'] if int(vehicle['modelYear']) == result['year']]
        possible_vehicles.sort(reverse=True, key=lambda vehicle: self.vehicle_aspect_match_score(' '.join(
            [vehicle['makeDescription'], vehicle['modelDescription'], vehicle['trimDescription']]), result['kbb_details']['vehicle_name']))
        chosen_vehicle = possible_vehicles[0]
        temp_year = chosen_vehicle['modelYear']
        temp_make = chosen_vehicle['makeDescription']
        temp_make_id = chosen_vehicle['makeCode']
        temp_model = chosen_vehicle['modelDescription']
        temp_model_id = chosen_vehicle['modelCode']

        # zip_code_response = yield scrapy.FormRequest(
        #     method='GET',
        #     url='https://instant-offers.services.carmax.com/store/zip',
        #     headers={
        #         "authority": "instant-offers.services.carmax.com",
        #         "accept": "application/json, text/plain, */*",
        #         "accept-language": "en-GB,en;q=0.9",
        #         "authorization": authorization,
        #         "content-type": "application/json",
        #         # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
        #         "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
        #         "kr": kr_key,
        #         "origin": "https://www.carmax.com",
        #         "referer": "https://www.carmax.com/",
        #         "sec-fetch-dest": "empty",
        #         "sec-fetch-mode": "cors",
        #         "sec-fetch-site": "same-site",
        #         # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
        #         # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        #     },
        #     formdata={
        #         'zipCode': result['zip_code'],
        #     },
        # )

        start_offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url=f'https://instant-offers.services.carmax.com/quote/start?make={temp_make}&model={temp_model}&year={temp_year}&vin={result["vin_number"]}&zipcode={result["zip_code"]}&upgrade=false&async=false',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
            data={},
        )

        quote_id = start_offer_response.json()['quoteId']
        isEligible = start_offer_response.json()['isEligible']
        isPicsyEligible = start_offer_response.json()['isPicsyEligible']
        if not isEligible or not isPicsyEligible:
            result['success'] = f"We'd like to see your {temp_make} {temp_model}"
            yield result
        styles_response = yield scrapy.Request(
            method='GET',
            url=f'https://instant-offers.services.carmax.com/vehiclespec/years/{temp_year}/makes/{temp_make_id}/models/{temp_model_id}/styles/vin/{result["vin_number"]}',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        styles = styles_response.json()

        matching_styles = styles['matchingStyles']
        remaining_styles = styles['remainingStyles']
        all_styles = matching_styles + remaining_styles

        def vehicle_name(style):
            return ' '.join(name for name in [
                style['make']['text'],
                style['model']['text'],
                style['description'],
                style['transmission']['text'],
                style['fuelType']['text'],
                style['drive']['text'],
                str(style['cylinderCount'])
            ] if name is not None)

        # Choose vehicle again now with more information
        possible_styles = [
            style for style in all_styles if style['modelYear'] == result['year']]
        possible_styles.sort(reverse=True, key=lambda style: self.vehicle_aspect_match_score(
            vehicle_name(style), result['kbb_details']['vehicle_name']))
        chosen_style = possible_styles[0]

        style_id = chosen_style['id']

        style_response = yield scrapy.Request(
            method='GET',
            url=f'https://instant-offers.services.carmax.com/vehiclespec/styles/{style_id}',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
        )

        style = style_response.json()

        year = style['year']['text']
        year_id = style['year']['code']
        make = style['make']['text']
        make_id = style['make']['code']
        model = style['model']['text']
        model_id = style['model']['code']
        trim = style['trim']['text']
        trim_id = style['trim']['code']
        # body_type = style['body']['text']
        body_type_id = style['body']['code']
        drivetrain = style['drive']['text']
        transmission = 'Automatic' if 'automatic' in result['transmission'].lower(
        ) else 'Manual'  # style['transmission']['text']
        standard_features = [{'code': feature['code'], 'description': feature['text']}
                             for feature in style['standardOptions']]
        available_features = [{'code': feature['code'], 'description': feature['text']}
                              for feature in style['availableOptions']]
        feature_ids = [feature['code'] for feature in standard_features]

        offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://instant-offers.services.carmax.com/quote/request',
            headers={
                "authority": "instant-offers.services.carmax.com",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "authorization": authorization,
                "content-type": "application/json",
                # "correlationid": "b5b915ea-e8f3-4199-9c23-9778431c2520",
                "icoexperiments": ";condition-question-email;kbb-valuation;photo-capture;suyc-control;suyc-desktop",
                "kr": kr_key,
                "origin": "https://www.carmax.com",
                "referer": "https://www.carmax.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                # "traceparent": "00-b8a230a55fe46446d33abe33c9956d37-1bc68dec6e66986f-01",
                # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            },
            data={
                "vehicleInfo": {
                    "isComplete": True,
                    "vin": result['vin_number'],
                    "plate": "",
                    "state": "",
                    "mileage": None,
                    "zipcode": result['zip_code'],
                    "styleCode": style_id,
                    "profile": {
                        "year": str(year),
                        "yearCode": year_id,
                        "make": make,
                        "makeCode": make_id,
                        "model": model,
                        "modelCode": model_id,
                        "trim": trim,
                        "trimCode": trim_id,
                        "bodyCode": body_type_id
                    }
                },
                "featureInfo": {
                    "isComplete": True,
                    "style": {
                        "id": style_id,
                        "description": None
                    },
                    "drive": drivetrain,
                    "driveDisplay": None,
                    "transmission": transmission,
                    "transmissionDisplay": None,
                    "features": feature_ids
                },
                "featureLookupInfo": {
                    "year": str(temp_year),
                    "makeCode": temp_make_id,
                    "modelCode": temp_model_id,
                    "availableStyles": [],
                    "matchingStyles": matching_styles,
                    "remainingStyles": remaining_styles,
                    "standardFeatures": standard_features,
                    "availableFeatures": available_features,
                    "stylesByVin": {
                        "matchingStyles": matching_styles,
                        "remainingStyles": remaining_styles
                    }
                },
                "conditionInfo": {
                    "conditionAnswers": [
                        {
                            "questionCode": 100,
                            "questionValue": "Has the vehicle ever been in an accident?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "answers": [],
                            "questionCode": 110,
                            "questionValue": "How many fender benders?"
                        },
                        {
                            "answers": [],
                            "questionCode": 120,
                            "questionValue": "How many serious accidents?"
                        },
                        {
                            "questionCode": 910,
                            "questionValue": "Does the vehicle have any frame damage?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 920,
                            "questionValue": "Does the vehicle have any flood damage?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 830,
                            "questionValue": "Has this vehicle been smoked in?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 200,
                            "questionValue": "Are there any mechanical issues or warning lights displayed on the dashboard?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "answers": [],
                            "questionCode": 210,
                            "questionValue": "Is the vehicle inoperable or does it have problems running?"
                        },
                        {
                            "answers": [],
                            "questionCode": 220,
                            "questionValue": "Are there engine issues?"
                        },
                        {
                            "answers": [],
                            "questionCode": 230,
                            "questionValue": "Are there transmission issues?"
                        },
                        {
                            "answers": [],
                            "questionCode": 240,
                            "questionValue": "Are any of these warning lights displayed on the dashboard? (select all that apply)"
                        },
                        {
                            "answers": [],
                            "questionCode": 251,
                            "questionValue": "Do any of the following apply? (select all that apply)"
                        },
                        {
                            "questionCode": 1000,
                            "questionValue": "Has the odometer ever been broken or replaced?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 300,
                            "questionValue": "Are there any panels in need of paint or body work?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 320,
                            "questionValue": "Any major rust and/or hail damage?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "answers": [],
                            "questionCode": 310,
                            "questionValue": "Select all that apply"
                        },
                        {
                            "questionCode": 410,
                            "questionValue": "Are any interior parts broken or inoperable?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 420,
                            "questionValue": "Are there any rips, tears, or stains in the interior?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 500,
                            "questionValue": "Do any tires need to be replaced?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "questionCode": 600,
                            "questionValue": "How many keys do you have?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "2 or more"
                                }
                            ]
                        },
                        {
                            "questionCode": 700,
                            "questionValue": "Does the vehicle have any aftermarket modifications?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "answers": [],
                            "questionCode": 710,
                            "questionValue": "Have aftermarket suspension changes been made (lift/lowering kits, shock absorbers, etc.)?"
                        },
                        {
                            "answers": [],
                            "questionCode": 720,
                            "questionValue": "Have engine modifications been made?"
                        },
                        {
                            "questionCode": 800,
                            "questionValue": "Are there any other issues with the vehicle?",
                            "answers": [
                                {
                                    "answerCode": 1,
                                    "answerValue": "No"
                                }
                            ]
                        },
                        {
                            "answers": [],
                            "questionCode": 810,
                            "questionValue": "Is the convertible top broken or in need of repair?"
                        },
                        {
                            "answers": [],
                            "questionCode": 820,
                            "questionValue": "Are there any problems with the Air Conditioning?"
                        },
                        {
                            "answers": [],
                            "questionCode": 840,
                            "questionValue": "Is any standard equipment missing (wheels, 3rd row seat, etc.)?"
                        }
                    ],
                    "isComplete": True,
                    "mileage": f'{result["mileage"]:,}',
                    "errorCount": 0
                },
                "ciamId": None,
                "visitorId": None,
                "formMetadata": {
                    "querystring": {},
                    "startingMethod": "VIN"
                },
                "quoteId": quote_id,
                "customerInfo": {
                    "email": result['email']
                },
                "enabledFeatures": offer_features,
                "reCaptchaToken": "",
            },
        )

        offer = offer_response.json()

        if offer['offerSuccessful']:
            result['price'] = float(offer['offer']['offerAmount'])

        elif offer['offer']['declineReason'] == 'offer_exceeds_upper_limit':
            result['success'] = 'We\'d like to see your {make} {model}. We handle high-value cars like yours in person.'

        else:
            # decline_reason = offer['offer']['declineReason']
            result['success'] = f"We'd like to see your {make} {model}"

        yield result
