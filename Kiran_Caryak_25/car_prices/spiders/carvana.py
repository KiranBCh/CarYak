import scrapy
import scrapy.http
import re
from typing import Any, cast
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesCarvanaSpider(car_prices_spider(source='Carvana')):
    site_conditions = {
        'bad': 'Kind Of Rough',
        'moderate': 'Just Okay',
        'good': 'Pretty Great',
        'excellent': 'Pretty Great',
    }

    condition_codes = {
        'bad': 'ROUGH',
        'moderate': 'OKAY',
        'good': 'GREAT',
        'excellent': 'GREAT',
    }

    def answers_to_offer_questions(self, condition):
        return {
            "Sell or Trade In?": "Sell",
            "Do you currently have a loan or lease on your vehicle?": "Neither",
            "Has your vehicle been in an accident?": "No Accidents",
            "Does your vehicle have any issues that would stop us from driving it?": "Drivable",
            "Mechanical & Electrical Issues": "No Mechanical Or Electrical Issues",
            "Exterior Damage": "No Exterior Damage",
            "Interior Damage": "No Interior Damage",
            "Does your vehicle have any modifications (eg suspension, engine, etc)?": "No Modifications",
            "Has your vehicle been smoked in?": "Not Smoked In",
            "How many keys do you have for this vehicle?": "2+ Keys",
            "What is the best way to describe your vehicle's overall condition?": self.site_conditions[condition],
        }

    def process_requests(self, result):
        condition = result['condition']
        result['answers'] = self.answers_to_offer_questions(condition)

        session_response = yield scrapy.Request(
            url=f'https://www.carvana.com/sell-my-car',
            callback=self.parse_cookie_response,
        )

        session_id = cast(list[Any], re.match(
            r'BrowserCookieId=(.+?);', session_response[0].decode()))[1]

        vin_response = yield scrapy.Request(
            url=f'https://apik.carvana.io/stc/trades/api/v1/vehicleconfiguration/kbbvinlookup/{result["vin_number"]}',
            callback=self.parse_json_response,
        )

        years = {item['displayName']: item for item in vin_response}
        year_item = years[str(result['year'])]
        year = year_item['displayName']

        makes = {item['displayName']: item for item in year_item['makes']}
        make_item = makes[result['make']]
        make = make_item['displayName']

        models = {item['displayName']: item for item in make_item['models']}
        model_item = models[result['model']]
        model = model_item['displayName']

        trims = {item['displayName']: item for item in model_item['trims']}
        trim_item = trims[result['trim']]
        trim = trim_item['displayName']
        trim_id = trim_item['kbbId']

        engines = {item['displayName']: item for item in trim_item['engines']}
        engine_item = engines[result['engine']]
        engine_id = engine_item['optionId']

        transmissions = {item['displayName']                         : item for item in trim_item['transmissions']}
        transmission_item = transmissions[result['transmission']]
        transmission_id = transmission_item['optionId']

        drivetrains = {item['displayName']                       : item for item in trim_item['drivetrains']}
        drivetrain_item = drivetrains[result['drivetrain']]
        drivetrain_id = drivetrain_item['optionId']

        '''
        options_response = yield scrapy.Request(
            url=f'https://apik.carvana.io/stc/trades/api/v1/vehicleconfiguration/getpowertrainoptionsbyid/{trim_id}',
            callback=self.parse_json_response,
        )

        engines = options_response['engines']
        transmissions = options_response['transmissions']
        drivetrains = options_response['drivetrains']

        engine_id = next(engine['optionId'] for engine in engines if engine['isDefault'] == True)
        transmission_id = next(transmission['optionId'] for transmission in transmissions if transmission['isDefault'] == True)
        drivetrain_id = next(drivetrain['optionId'] for drivetrain in drivetrains if drivetrain['isDefault'] == True)
        '''

        location_response = yield scrapy.Request(
            url=f'https://apik.carvana.io/stc/trades/api/v3/address/hub/{result["zip_code"]}/tradedropoff',
            callback=self.parse_json_response,
        )

        miles_to_nearest_branch = location_response['content']['drivingMiles']

        site_condition = self.condition_codes[result["condition"]]

        offer_request_data = {
            'query': '\n  mutation submitAppraisal(\n    $vehicleVinInput: CreateVehicleVinInput!\n    $plateStateInput: SetPlateStateInput!\n    $odometerInput: SetOdometerInput!\n    $zipCodeInput: SetZipCodeInput!\n    $drivingMilesToHubInput: SetDrivingMilesToHubInput!\n    $vehicleColorInput: VehicleColorInput!\n    $powertrainInput: SetPowertrainInput!\n    $premiumOptionsInput: SetPremiumOptionsInput!\n    $vehicleQuestionsInput: SetVehicleQuestionsInput!\n    $leadInput: OfferLeadInput!\n  ) {\n    createVehicleByVin(input: $vehicleVinInput) {\n      value\n    }\n    setPlateState(input: $plateStateInput){\n      value\n    }\n    setOdometer(input: $odometerInput) {\n      value\n    }\n    setZipCode(input: $zipCodeInput) {\n      value\n    }\n    setDrivingMilesToHub(input: $drivingMilesToHubInput) {\n      value\n    }\n    setVehicleColor(input: $vehicleColorInput) {\n      value\n    }\n    setPowertrain(input: $powertrainInput){\n      value\n    }\n    setPremiumOptions(input: $premiumOptionsInput){\n      value\n    }\n    setVehicleQuestions(input: $vehicleQuestionsInput) {\n      value\n    }\n    setAppraisalLead(input: $leadInput) {\n      value\n    }\n    createAppraisal {\n      appraisalId\n      offerValue\n      appraisalUrl\n      isVinVerified\n      unsupportedStatus\n      vehicleId\n    }\n  }\n',
            'variables': {
                'vehicleVinInput': {
                    'vin': result['vin_number'],
                    'configuration': {
                        'year': int(year),
                        'model': model,
                        'make': make,
                        'trim': trim,
                    },
                },
                'plateStateInput': {},
                'odometerInput': {
                    'odometer': result['mileage'],
                },
                'zipCodeInput': {
                    'zipCode': result['zip_code'],
                },
                'drivingMilesToHubInput': {
                    'drivingMiles': miles_to_nearest_branch,
                },
                'vehicleColorInput': {
                    'colorId': 2,
                },
                'powertrainInput': {
                    'engine': engine_id,
                    'transmission': transmission_id,
                    'drivetrain': drivetrain_id,
                },
                'premiumOptionsInput': {
                    'options': [],
                },
                'vehicleQuestionsInput': {
                    'accidentCount': 'NONE',
                    'aftermarketParts': False,
                    'drivable': True,
                    'estimatedRepairCost': None,
                    'exteriorDamages': [],
                    'interiorDamages': [],
                    'keyCount': 'TWO_PLUS',
                    'lien': 'NONE',
                    'mechanicalDefects': [],
                    'physicalCondition': site_condition,
                    'smokedIn': False,
                    'tradeIntent': 'SELL',
                },
                'leadInput': {
                    'leadSourceId': 0,
                    'email': result['email'],
                    'browserCookieId': session_id,
                },
            },
        }

        result['Accident count'] = offer_request_data['variables']['vehicleQuestionsInput']['accidentCount'].title()
        result['Aftermarket parts'] = offer_request_data['variables']['vehicleQuestionsInput']['aftermarketParts']
        result['Drivable'] = offer_request_data['variables']['vehicleQuestionsInput']['drivable']
        result['Estimated repair cost'] = offer_request_data['variables']['vehicleQuestionsInput']['estimatedRepairCost']
        result['List of exterior Damages'] = offer_request_data['variables']['vehicleQuestionsInput']['exteriorDamages']
        result['List of interior Damages'] = offer_request_data['variables']['vehicleQuestionsInput']['interiorDamages']
        result['Key count'] = '2+' if offer_request_data['variables']['vehicleQuestionsInput']['keyCount'] == 'TWO_PLUS' else '1'
        result['Lien'] = 'Fully paid for' if offer_request_data['variables']['vehicleQuestionsInput'][
            'lien'] == 'NONE' else offer_request_data['variables']['vehicleQuestionsInput'][''].title()
        result['List of mechanical defects'] = offer_request_data['variables']['vehicleQuestionsInput']['mechanicalDefects']
        result['Physical condition'] = offer_request_data['variables']['vehicleQuestionsInput']['physicalCondition'].title()
        result['Smoked in'] = offer_request_data['variables']['vehicleQuestionsInput']['smokedIn']
        result['Intent'] = offer_request_data['variables']['vehicleQuestionsInput']['tradeIntent'].title()

        offer_response = yield scrapy.http.JsonRequest(
            url=f'https://apik.carvana.io/stc/offer/graphql/',
            data=offer_request_data,
            callback=self.parse_json_response,
        )

        price = offer_response['data']['createAppraisal']['offerValue']
        if price is None:
            result['success'] = 'Needs Input from Appraisal Expert'
        else:
            result['price'] = float(price)
        yield result
