import scrapy
import scrapy.http
import re
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesKBBSpider(car_prices_spider(source='KBB')):
    special_character_except_dash_and_underscore_pattern = re.compile(
        r'[^a-zA-Z0-9_-]')

    site_conditions = {
        'bad': 'fair',
        'moderate': 'good',
        'good': 'verygood',
        'excellent': 'excellent',
    }

    def process_requests(self, result):
        condition = result['condition']

        vin_details = yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            callback=self.parse_json_response,
            data={
                'operationName': 'vinSLPPageCadsQuery',
                'variables': {
                    'vin': result['vin_number'],
                },
                'query': 'query vinSLPPageCadsQuery($vin: String, $license: String) {\n  vehicleUrlByVin: vehicleUrlByVinCads(vin: $vin, license: $license) {\n    usingCads\n    url\n    error\n    make\n    makeId\n    model\n    modelId\n    year\n    vin\n    __typename\n  }\n}',
            },
        )

        vehicle_data = vin_details['data']['vehicleUrlByVin']

        make = vehicle_data['make'].lower().replace(' ', '-')
        model = vehicle_data['model'].lower().replace(' ', '-')
        year = vehicle_data['year']

        trim_response = yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            callback=self.parse_json_response,
            data={
                'operationName': 'vinLicensePageCadsQuery',
                'variables': {
                    'make': make,
                    'model': model,
                    'year': year,
                    'vin': result['vin_number'],
                },
                'query': 'query vinLicensePageCadsQuery($year: String, $make: String, $model: String, $vin: String) {\n  ymm: vinLicensePageCads(\n    vehicleClass: \"UsedCar\"\n    year: $year\n    make: $make\n    model: $model\n    vin: $vin\n  ) {\n    usingCads\n    year\n    make {\n      id\n      name\n      __typename\n    }\n    model {\n      id\n      name\n      __typename\n    }\n    bodyStyles {\n      name\n      trims {\n        id\n        name\n        vehicleId\n        __typename\n      }\n      defaultVehicleId\n      __typename\n    }\n    typicalMileage\n    defaultVehicleId\n    subCategory\n    chromeStyleId\n    __typename\n  }\n}',
            },
        )

        trim_infos = [trim for body_style in trim_response['data']
                      ['ymm']['bodyStyles'] for trim in body_style['trims']]
        trim_names = [self.special_character_except_dash_and_underscore_pattern.sub(
            '', trim_info['name'].lower().replace(' ', '-')) for trim_info in trim_infos]

        trim_index = 0
        trim = trim_names[trim_index]
        vehicle_id = trim_infos[trim_index]['vehicleId']

        options_response = yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            callback=self.parse_json_response,
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'referer': f'https://www.kbb.com/{make}/{model}/{year}/?intent=trade-in-sell&vin={result["vin_number"].lower()}',
            },
            data={
                'operationName': 'vinLicenseVehicleDetailsCadsQuery',
                'variables': {
                    'vin': result['vin_number'],
                    'selectedVehicleId': int(vehicle_id),
                },
                'query': "query vinLicenseVehicleDetailsCadsQuery($vin: String, $selectedVehicleId: Int, $lp: String, $state: String) {\n  vinLicenseVehicleDetails: vinLicenseVehicleDetailsCads(\n    vin: $vin\n    selectedVehicleId: $selectedVehicleId\n    lp: $lp\n    state: $state\n  ) {\n    usingCads\n    vinResults {\n      vehicleOptionIds\n      vehicleId\n      __typename\n    }\n    selectedVehicle {\n      vehicleId\n      vehicleOptionIds\n      __typename\n    }\n    trims {\n      vehicleId\n      trimName\n      bodyStyle\n      __typename\n    }\n    vehicleOptionsData {\n      engine {\n        vehicleOptionId\n        optionName\n        __typename\n      }\n      transmission {\n        vehicleOptionId\n        optionName\n        __typename\n      }\n      drivetrain {\n        vehicleOptionId\n        optionName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
            },
        )

        selected_options = options_response['data']['vinLicenseVehicleDetails']['selectedVehicle']['vehicleOptionIds']
        vehicle_options = options_response['data']['vinLicenseVehicleDetails']['vehicleOptionsData']
        engine_options = [option['vehicleOptionId']
                          for option in vehicle_options['engine']]
        transmission_options = [option['vehicleOptionId']
                                for option in vehicle_options['transmission']]
        drivetrain_options = [option['vehicleOptionId']
                              for option in vehicle_options['drivetrain']]

        if len(set(engine_options).intersection(selected_options)) <= 0:
            selected_options.append(engine_options[0])

        if len(set(transmission_options).intersection(selected_options)) <= 0:
            selected_options.append(transmission_options[0])

        if len(set(drivetrain_options).intersection(selected_options)) <= 0:
            selected_options.append(drivetrain_options[0])

        colours_response = yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            callback=self.parse_json_response,
            data={
                'operationName': 'optionsPageQuery',
                'variables': {
                    'make': make,
                    'model': model,
                    'year': year,
                    'trim': trim,
                    'vehicleId': vehicle_id,
                    'initialOptions': '|'.join(f'{option}|true' for option in selected_options),
                },
                'query': 'query optionsPageQuery($year: String, $make: String, $model: String, $trim: String, $vehicleId: String, $initialOptions: String, $appUrl: String) {\n  ymmt: optionsPage(\n    vehicleClass: \"UsedCar\"\n    year: $year\n    make: $make\n    model: $model\n    trim: $trim\n    vehicleId: $vehicleId\n    appUrl: $appUrl\n  ) {\n    redirectUrl\n    vehicleId\n    subCategory\n    chromeStyleId\n    bodyStyle\n    year\n    searchNewCarYear\n    make {\n      id\n      name\n      __typename\n    }\n    model {\n      id\n      name\n      __typename\n    }\n    trim {\n      id\n      name\n      __typename\n    }\n    showCategoryStyleLink\n    typicalMileage\n    selectedOptions(initialOptions: $initialOptions) {\n      groups {\n        name\n        sections {\n          optionSectionName\n          required\n          options {\n            vehicleOptionId\n            optionName\n            categoryGroup\n            sortOrder\n            isTypical\n            isSelected\n            isConfigurable\n            hasRelationships\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      colors {\n        vehicleOptionId\n        optionName\n        categoryGroup\n        sortOrder\n        isTypical\n        isSelected\n        isConfigurable\n        hasRelationships\n        imageUrl\n        __typename\n      }\n      vrsSelectedOptions {\n        vehicleOptionId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            },
        )

        first_colour_option = colours_response['data']['ymmt']['selectedOptions']['colors'][0]['vehicleOptionId']
        selected_options.append(first_colour_option)

        offer_response = yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            callback=self.parse_json_response,
            data={
                'operationName': 'ymmtPageQuery',
                'variables': {
                    'make': make,
                    'model': model,
                    'year': year,
                    'trim': trim,
                    'intent': 'trade-in-sell',
                    'options': '|'.join(f'{option}|true' for option in selected_options),
                    'mileage': str(result['mileage']),
                    'zipcode': result['zip_code'],
                },
                'query': 'query ymmtPageQuery($year: String, $make: String, $model: String, $trim: String, $vehicleId: String, $intent: String, $options: String, $mileage: String, $zipcode: String, $appUrl: String) {\n  ymmt: ymmtPage(\n    vehicleClass: "UsedCar"\n    year: $year\n    make: $make\n    model: $model\n    trim: $trim\n    vehicleId: $vehicleId\n    intent: $intent\n    options: $options\n    mileage: $mileage\n    zipcode: $zipcode\n    appUrl: $appUrl\n  ) {\n    redirectUrl\n    vehicleId\n    year\n    make {\n      id\n      name\n      __typename\n    }\n    model {\n      id\n      name\n      __typename\n    }\n    trim {\n      id\n      name\n      __typename\n    }\n    showCategoryStyleLink\n    generationInstanceId\n    typicalMileage\n    bodyStyle\n    luxuryType\n    sportType\n    intent\n    subCategory\n    size\n    consumerReviews {\n      averageOverallRating\n      totalReviewCount\n      reviewsRoute\n      __typename\n    }\n    pricing\n    baseImageUrl\n    chromeStyleId\n    selectedOptionsData {\n      groups {\n        name\n        sections {\n          optionSectionName\n          required\n          options {\n            vehicleOptionId\n            optionName\n            categoryGroup\n            sortOrder\n            isTypical\n            isSelected\n            isConfigurable\n            hasRelationships\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      vrsSelectedOptions {\n        vehicleOptionId\n        optionName\n        categoryGroup\n        isTypical\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            },
        )

        site_condition = self.site_conditions[condition]

        prices = offer_response['data']['ymmt']['pricing']['tradein']

        result['price'] = prices[site_condition]

        yield result
