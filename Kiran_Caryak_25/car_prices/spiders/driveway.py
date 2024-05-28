from car_prices.exceptions import InvalidContactInfo
import scrapy
import scrapy.http
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesDrivewaySpider(car_prices_spider(source='Driveway')):
    api_key = 'e6c1852eb5124b1890fbd17ad53e870a'

    default_colours = [
        {
            "vifnum": -1,
            "code": "Black",
            "title": "Black",
            "simpletitle": "Black",
            "rgb1": "2D2926"
        },
        {
            "vifnum": -1,
            "code": "White",
            "title": "White",
            "simpletitle": "White",
            "rgb1": "FFFFFF"
        },
        {
            "vifnum": -1,
            "code": "Gray",
            "title": "Gray",
            "simpletitle": "Gray",
            "rgb1": "989898"
        },
        {
            "vifnum": -1,
            "code": "Silver",
            "title": "Silver",
            "simpletitle": "Silver",
            "rgb1": "DFE0DF"
        },
        {
            "vifnum": -1,
            "code": "Blue",
            "title": "Blue",
            "simpletitle": "Blue",
            "rgb1": "4173AD"
        },
        {
            "vifnum": -1,
            "code": "Red",
            "title": "Red",
            "simpletitle": "Red",
            "rgb1": "DA4548"
        },
        {
            "vifnum": -1,
            "code": "Brown",
            "title": "Brown",
            "simpletitle": "Brown",
            "rgb1": "75523E"
        },
        {
            "vifnum": -1,
            "code": "Beige",
            "title": "Beige",
            "simpletitle": "Beige",
            "rgb1": "CAB0A2"
        },
        {
            "vifnum": -1,
            "code": "Gold",
            "title": "Gold",
            "simpletitle": "Gold",
            "rgb1": "C18F55"
        },
        {
            "vifnum": -1,
            "code": "Green",
            "title": "Green",
            "simpletitle": "Green",
            "rgb1": "74885B"
        },
        {
            "vifnum": -1,
            "code": "Yellow",
            "title": "Yellow",
            "simpletitle": "Yellow",
            "rgb1": "FDB853"
        },
        {
            "vifnum": -1,
            "code": "Orange",
            "title": "Orange",
            "simpletitle": "Orange",
            "rgb1": "D87A3F"
        },
        {
            "vifnum": -1,
            "code": "Pink",
            "title": "Pink",
            "simpletitle": "Pink",
            "rgb1": "F7B7B6"
        },
        {
            "vifnum": -1,
            "code": "Burgundy",
            "title": "Burgundy",
            "simpletitle": "Burgundy",
            "rgb1": "771A17"
        },
        {
            "vifnum": -1,
            "code": "Bronze",
            "title": "Bronze",
            "simpletitle": "Bronze",
            "rgb1": "A3492E"
        },
        {
            "vifnum": -1,
            "code": "Purple",
            "title": "Purple",
            "simpletitle": "Purple",
            "rgb1": "6D4789"
        },
        {
            "vifnum": -1,
            "code": "Tan",
            "title": "Tan",
            "simpletitle": "Tan",
            "rgb1": "BCB295"
        },
        {
            "vifnum": -1,
            "code": "Turquoise",
            "title": "Turquoise",
            "simpletitle": "Turquoise",
            "rgb1": "53BBB2"
        },
        {
            "vifnum": -1,
            "code": "Other",
            "title": "Other",
            "simpletitle": "Other",
            "rgb1": "FFFFFF"
        }
    ]

    site_conditions = {
        'bad': 'Poor',
        'moderate': 'Fair',
        'good': 'Good',
        'excellent': 'Great',
    }

    condition_codes = {
        'bad': 'POOR',
        'moderate': 'FAIR',
        'good': 'GOOD',
        'excellent': 'GREAT',
    }

    def answers_to_offer_questions(self, condition):
        return {
            'What is the condition of the car?': self.site_conditions[condition],
            'Are there active warning lights?': 'No',
            'Has the car been in an accident?': 'No',
            'Has the car been smoked in?': 'No',
            'Any active loan or lease on the car?': 'None',  # Loan, Lease
            'How many keys are available?': '2',  # 1
        }

    def process_requests(self, result):
        condition = result['condition']
        result['answers'] = self.answers_to_offer_questions(condition)

        vin_decoded_response = yield scrapy.FormRequest(
            method='GET',
            url='https://api-gateway.driveway.com/sell/v8/vehicle',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.driveway.com/",
                "Content-Type": "application/json",
                # "x-datadog-origin": "rum",
                # "x-datadog-parent-id": "2538893234299905467",
                # "x-datadog-sampled": "1",
                # "x-datadog-sampling-priority": "1",
                # "x-datadog-trace-id": "9213211847105252849",
                "Origin": "https://www.driveway.com",
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
                'vin': result['vin_number'],
                'key': self.api_key,
            },
        )

        vin_decoded = vin_decoded_response.json()

        year = vin_decoded['year']
        make = vin_decoded['make']
        model = vin_decoded['model']
        vehicle_options = vin_decoded['options']
        available_trims = vin_decoded['availableTrims']

        trim_candidates = available_trims.copy()
        trim_candidates.append(vin_decoded['selectedTrim'])
        trim_candidates.sort(reverse=True, key=lambda trim: self.vehicle_aspect_match_score(
            ' '.join([make, model, trim['name']]), result['kbb_details']['vehicle_name']))

        selected_trim = trim_candidates[0]

        def get_colour_and_image():
            vehicle_colours_response = yield scrapy.FormRequest(
                method='GET',
                url='https://api-gateway.driveway.com/sell/v8/vehicle/colors',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.driveway.com/",
                    "Content-Type": "application/json",
                    # "x-datadog-origin": "rum",
                    # "x-datadog-parent-id": "2941184500020059207",
                    # "x-datadog-sampled": "1",
                    # "x-datadog-sampling-priority": "1",
                    # "x-datadog-trace-id": "4375989607188606296",
                    "Origin": "https://www.driveway.com",
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
                    'vifnum': str(selected_trim['vifnum']),
                    'key': self.api_key
                }
            )

            vehicle_colours = vehicle_colours_response.json()
            colour = next(
                (colour for colour in vehicle_colours if colour['simpletitle'] == 'Black'), vehicle_colours[0])

            vehicle_image_response = yield scrapy.FormRequest(
                method='GET',
                url='https://api-gateway.driveway.com/sell/v8/vehicle/image',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.driveway.com/",
                    "Content-Type": "application/json",
                    # "x-datadog-origin": "rum",
                    # "x-datadog-parent-id": "5905684934655685202",
                    # "x-datadog-sampled": "1",
                    # "x-datadog-sampling-priority": "1",
                    # "x-datadog-trace-id": "1081346436394978208",
                    "Origin": "https://www.driveway.com",
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
                    'vifnum': str(colour['vifnum']),
                    'colorCode': colour['code'],
                    'key': self.api_key,
                }
            )

            vehicle_image_url = vehicle_image_response.json().get(
                'url', '/assets/placeholder-car.png')

            return colour, vehicle_image_url

        colour, vehicle_image_url = (yield from get_colour_and_image()) if selected_trim.get('vifnum', None) else (next(
                (colour for colour in self.default_colours if colour['simpletitle'] == 'Black')), '/assets/placeholder-car.png')

        dealership_distance_response = yield scrapy.FormRequest(
            method='GET',
            url='https://api-gateway.driveway.com/sell/v8/distance',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.driveway.com/",
                "content-type": "application/json",
                # "x-datadog-origin": "rum",
                # "x-datadog-parent-id": "5482331614434420903",
                # "x-datadog-sampled": "1",
                # "x-datadog-sampling-priority": "1",
                # "x-datadog-trace-id": "5816384999427969832",
                "Origin": "https://www.driveway.com",
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
                'postalCode': result['zip_code'],
                'key': self.api_key,
            }
        )

        dealership_distance = dealership_distance_response.json()
        within_market = dealership_distance['withinRange']
        nearby_dealerships = dealership_distance['dealershipsNearby']
        nearest_dealership_code = nearby_dealerships[0]['code'] if len(
            nearby_dealerships) > 0 else 'undefined'

        offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url=f'https://api-gateway.driveway.com/sell/v8/offer?dealershipCode={nearest_dealership_code}&saleType=SELL&key={self.api_key}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.driveway.com/",
                "content-type": "application/json",
                # "x-datadog-origin": "rum",
                # "x-datadog-parent-id": "5063001631272706100",
                # "x-datadog-sampled": "1",
                # "x-datadog-sampling-priority": "1",
                # "x-datadog-trace-id": "1908657620181187426",
                "Origin": "https://www.driveway.com",
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
                "postalCode": result['zip_code'],
                "email": result['email'],
                "phone": result['phone_number'],
                "firstName": result['first_name'],
                "lastName": result['last_name'],
                "location": {
                    "postalCode": result['zip_code'],
                    "distanceInMiles": 0,
                    "withinMarket": within_market
                },
                "inspectionPreferences": {
                    "location": None,
                    "contactPreference": "EMAIL"
                },
                "vehicle": {
                    "vin": result['vin_number'],
                    "year": year,
                    "make": make,
                    "model": model,
                    "availableTrims": available_trims,
                    "selectedTrim": selected_trim,
                    "selectedColor": colour,
                    "options": vehicle_options,
                    "availableColors": self.default_colours,
                    "imageUrl": vehicle_image_url,
                    "condition": {
                        "overallCondition": self.condition_codes[condition],
                        "mileage": result['mileage'],
                        "warningLights": False,
                        "accidents": False,
                        "smokedIn": False,
                        "activeFinance": {
                            "type": "NOT_PROVIDED",
                            "estimatedRemaining": 0,
                            "lenderId": ""
                        },
                        "numKeys": "MULTIPLE"
                    }
                }
            },
        )

        offer = offer_response.json()

        if 'lead' in offer:
            lead = offer['lead']
            result['User give condition'] = self.site_conditions[condition]
            result['What is the condition of the car?'] = lead['vehicle']['condition']['overallCondition']
            result['Any active loan or lease on the car?'] = lead['vehicle']['condition']['activeFinance']['type']
            result['Has the car been in an accident?'] = 'No'
            result['Are there active warning lights?'] = 'No'
            result['Has the car been smoked in?'] = 'No'
            result['How many keys are available?'] = 2

            result['InspectionPreferences'] = lead['inspectionPreferences']
            result['location'] = lead['location']
            result['selectedTrim'] = lead['vehicle']['selectedTrim']
            result['selectedColor'] = lead['vehicle']['selectedColor']
            result['OptionVehicles'] = lead['vehicle']['options']
            result['condition'] = lead['vehicle']['condition']
            result['offer'] = lead['offer']
            result['status'] = offer['status']
            result['saleType'] = offer['saleType']
            result['userAction'] = offer['userAction']
            result['dealershipCode'] = offer['dealershipCode']
            result['paymentDetails'] = offer['paymentDetails']

            if lead['offer']['noPrice']:
                result['success'] = 'Our team will call you shortly with your offer!'
            else:
                result['price'] = float(lead['offer']['offerAmount'])

            yield result

        else:
            error_messages = [error['message'] for error in offer['errors']]
            self.logger.error(f'The site returned errors while scraping. Here is what the site says: {error_messages}')

            if 'Invalid email provided' in error_messages:
                raise InvalidContactInfo()

            else:
                result['success'] = 'Our team will call you shortly with your offer!'

                yield result
