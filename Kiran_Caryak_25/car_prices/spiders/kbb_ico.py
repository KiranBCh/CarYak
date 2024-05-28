from typing import cast
from car_prices.exceptions import ContactInfoInUse, CantMakeOfferForVin, InvalidContactInfo, OfferUnderReview
import scrapy
import scrapy.http
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesKBBICOSpider(car_prices_spider(source='KBB_ICO')):
    site_conditions = {
        'bad': [
            'Front Bumper Major scratches',
            'Rear Bumper Major scratches',
            'Trunk Major scratches',
            'Roof Major scratches',
            'Driver-side Front Door Major scratches',
            'Driver-side Front Fender Major scratches',
            'Driver-side Rear Door Major scratches',
            'Driver-side Rocker Panel Major scratches',
            'Driver-side Rear Panel Major scratches',
            'Hood Major scratches',
        ],
        'moderate': [
            'Front Bumper Major scratches',
            'Rear Bumper Major scratches',
            'Trunk Major scratches',
            'Roof Major scratches',
        ],
        'good': [
            'Front Bumper Major scratches',
            'Rear Bumper Major scratches',
            'Trunk Major scratches',
        ],
        'excellent': [
        ],
    }

    condition_codes = {
        'Front Bumper Major scratches': {'questionId': 'qc/20391', 'value': True, 'type': 'ToggleSelect'},
        'Rear Bumper Major scratches': {'questionId': 'qc/20392', 'value': True, 'type': 'ToggleSelect'},
        'Trunk Major scratches': {'questionId': 'qc/20105', 'value': True, 'type': 'ToggleSelect'},
        'Roof Major scratches': {'questionId': 'qc/20099', 'value': True, 'type': 'ToggleSelect'},
        'Driver-side Front Door Major scratches': {'questionId': 'qc/20066', 'value': True, 'type': 'ToggleSelect'},
        'Driver-side Front Fender Major scratches': {'questionId': 'qc/20072', 'value': True, 'type': 'ToggleSelect'},
        'Driver-side Rear Door Major scratches': {'questionId': 'qc/20069', 'value': True, 'type': 'ToggleSelect'},
        'Driver-side Rocker Panel Major scratches': {'questionId': 'qc/20075', 'value': True, 'type': 'ToggleSelect'},
        'Driver-side Rear Panel Major scratches': {'questionId': 'qc/20078', 'value': True, 'type': 'ToggleSelect'},
        'Hood Major scratches': {'questionId': 'qc/20096', 'value': True, 'type': 'ToggleSelect'},
    }

    api_key = 'kehj9w5vxkt4t8yugn5zkpey'

    def answers_to_offer_questions(self, condition):
        return {
            'Do you have 2 or more keys or keyless remotes?': 'Yes',
            'Has your vehicle had any modifications?': 'No',
            'Conditions': self.site_conditions[condition],
        }

    def process_requests(self, result):
        condition = result['condition']
        result['answers'] = self.answers_to_offer_questions(condition)
        public_ip_address = result['public_ip_address']

        autocheck_data = {
            'auctionAnnouncementWithin45Days': False,
            'floodDamage': False,
            'frameDamage': False,
            'hasAccidents': False,
            'isAutoCheckEligible': True,
            'isOriginalOwner': True,
            'usedAsRentalCar': False,
            'salvage': False,
            'titleBrand': False,
            'previouslyCanadian': False,
            'miles': result['mileage'],
        } | result['autocheck_data']

        eligibility_response = yield scrapy.FormRequest(
            method='GET',
            url='https://api.kbb.com/ico/v1/vehicles/eligibility',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.kbb.com/",
                "QuestionConversion": "fury",
                # "TraceId": "ccc1f5b4-f732-48ab-8f8d-1f0e1f47901f",
                "Content-Type": "text/json",
                "Origin": "https://www.kbb.com",
                # "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
            },
            formdata={
                'trimId': str(result['kbb_details']['trim']['trimId']),
                'api_key': self.api_key,
            },
        )

        vin_not_eligible = not cast(dict, eligibility_response.json())['data']['isEligible']

        if vin_not_eligible:
            self.logger.error('This vehicle isn\'t eligible for an Instant Cash Offer.')
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)


        selected_vehicle = result['kbb_details']

        year_id = selected_vehicle['year']['yearId']
        make_id = selected_vehicle['make']['makeId']
        model_id = selected_vehicle['model']['modelId']
        trim_id = selected_vehicle['trim']['trimId']
        chosen_colours = [colour['optionId'] for colour in selected_vehicle['colors']
                          if colour['displayName'] == result['colour']]
        colour_id = chosen_colours[0] if len(
            chosen_colours) > 0 else selected_vehicle['colors'][0]['optionId']
        engine_id = next(engine['engineId'] for engine in selected_vehicle['engines']
                         if engine['displayName'] == result['engine'])
        transmission_id = next(transmission['transmissionId'] for transmission in selected_vehicle['transmissions']
                               if transmission['displayName'] == result['transmission'])
        drivetrain_id = next(drivetrain['drivetrainId'] for drivetrain in selected_vehicle['drivetrains']
                             if drivetrain['displayName'] == result['drivetrain'])

        prospect_response = yield scrapy.http.JsonRequest(
            url=f'https://api.kbb.com/ico/v1/prospects?a=b&api_key={self.api_key}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'text/json',
                'Referer': 'https://www.kbb.com/instant-cash-offer/',
                'QuestionConversion': 'fury',
                # 'TraceId': '65ab7999-b69f-45d8-a4b0-ca5dc06339b9',
            },
            data={
                'vehicle': {
                    'yearId': year_id,
                    'makeId': make_id,
                    'modelId': model_id,
                    'trimId': trim_id,
                    'colorId': colour_id,
                    'transmissionId': transmission_id,
                    'engineId': engine_id,
                    'drivetrainId': drivetrain_id,
                    'vin': result['vin_number'],
                },
                'mileage': result['mileage'],
                'contactInfo': {},
                'isConsumerOffer': True,
                'channelId': 'e8f21a4b-7b53-4004-a5ee-21b35d4ed06c',
                'vehicleBuildDataFlags': {
                    'cadsUsed': selected_vehicle['cadsUsed'],
                    'transmissionsVinVerified': selected_vehicle['transmissionsVinVerified'],
                    'enginesVinVerified': selected_vehicle['enginesVinVerified'],
                    'drivetrainsVinVerified': selected_vehicle['drivetrainsVinVerified'],
                    'optionsVinVerified': selected_vehicle['optionsVinVerified'],
                    'colorsVinVerified': selected_vehicle['colorsVinVerified'],
                },
            },
        )

        prospect_doc = prospect_response.json()

        if 'prospectId' not in prospect_doc:
            if 400001 in prospect_doc['meta']['codes']:
                message = prospect_doc['meta']['links'][0]['properties']['message'] if len(prospect_doc['meta']['links']) else 'must have a maximum value of 1000000'
                self.logger.error(message)
                raise CantMakeOfferForVin(needs_to_see_vehicle=False)

        prospect_id = prospect_doc['data']['prospectId']

        yield scrapy.Request(
            method='PATCH',
            url=f'https://api.kbb.com/ico/v1/prospects/{prospect_id}/options?updateTED=false&api_key={self.api_key}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'text/json',
                'Referer': 'https://www.kbb.com/instant-cash-offer/',
                'QuestionConversion': 'fury',
                # 'TraceId': '65ab7999-b69f-45d8-a4b0-ca5dc06339b9',
            },
            body='[]'.encode(),
        )

        captcha_result = yield from self.solving_recaptchav2_coroutine(
            website_url='https://www.kbb.com/instant-cash-offer/',
            website_key='6Lcw624UAAAAABHAarQigBrISZ8455WfqSKv_0EI',
            proxy=result['proxy']
        )

        captcha_solution_token = captcha_result

        yield scrapy.http.JsonRequest(
            url=f'https://api.kbb.com/ico/v1/recaptcha/verify?a=b&api_key={self.api_key}',
            headers={
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'text/json',
                'Referer': 'https://www.kbb.com/instant-cash-offer/',
                'QuestionConversion': 'fury',
                # 'TraceId': '65ab7999-b69f-45d8-a4b0-ca5dc06339b9',
            },
            data={
                "ResponseToken": captcha_solution_token,
                # "ResponseToken": 'gRecaptchaResponse":"03AFY_a8ULO58W09ibFvFX4OuhKRBdB--vUsbcJLtGg_4q8oh74AnaPXeufx8erBXnO4VLOwSbb0Lb6wqwpXhspV0rNNLuVQSnVVRHeApbfZPO8cBYS23ViX2kYd_RZOxmt2LUYkLdbMdS_xuGnwzUOnyCNzuBrigPylBJ0GvHEN_tAQqlgRiBw4j2KWVwemlKCQ0uqJjXb0k3qW_b21AuIwbYy37wKFS1BiSrfAGjOdu692n11qrFlNO1yOpH2vKw093dPHWiz2UokjLa04r_COzoBciyfomGGg-xCL5Fhr9_sK4XHiTrAKjjHC1_Uw1iSqY_YB5efcL6RQ483GhsU8PFUBev1B9F6sBFSdWNedUqYXV9i0PgxVCY9WPc9WEk2ql3I7PgA_vXzMQEYbguTi40P0lVJitiKRtvq1qW-u6NpPzgUASpkyqa7AVm2Zi5dbNvV8bQu6lYV3kz1GkY0ZYzMnVTPa5w2FFlcVBUjcTtLQkTLBDn0-ng1ZQINFhv0ZIQVdJn7xU62F1eOk1A-hQDBf6NlyfSN2pIQQTnyJHCBVfSxYmd50_J0vl4nktGzz8w-1RyRCrbGg4t44Y4KXKIIM3gDYXuNl_hCrTBRn_1J2ha2XHT1Mw', },
            },
        )

        prospect_questions_response = yield scrapy.Request(
            url=f'https://api.kbb.com/ico/v1/prospects/{prospect_id}/documents?a=b&api_key={self.api_key}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'text/json',
                'referer': 'https://www.kbb.com/instant-cash-offer/',
                'questionconversion': 'fury',
            },
        )

        prospect_questions = {question['questionId']: question for question_type in prospect_questions_response.json()['data']['documents']
                              if question_type['canonicalName'] not in ['contactInfo', 'replacementVehicle/supplement'] for question in question_type['items']}

        yield scrapy.http.JsonRequest(
            method='PUT',
            url=f'https://api.kbb.com/ico/v1/prospects/{prospect_id}/answers?a=b&api_key={self.api_key}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'text/json',
                'Referer': 'https://www.kbb.com/instant-cash-offer/',
                'QuestionConversion': 'fury',
                # 'TraceId': '65ab7999-b69f-45d8-a4b0-ca5dc06339b9',
            },
            data={
                'bulkAnswers': [
                    {
                        'canonicalName': 'history',
                        'answers': [
                            {
                                'questionId': 'qp/65',
                                'value': False,
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/82',
                                'value': False,
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/76',
                                'value': False,
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/17',
                                'value': True,
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/81',
                                'value': autocheck_data['auctionAnnouncementWithin45Days'],
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/124',
                                'value': 'Yes' if autocheck_data['hasAccidents'] else 'No',
                                'type': 'Enum',
                            },
                            {
                                'questionId': 'qp/83',
                                'value': autocheck_data['isOriginalOwner'],
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/125',
                                'value': autocheck_data['usedAsRentalCar'],
                                'type': 'Boolean',
                            },
                            {
                                'questionId': 'qp/79',
                                'value': result['answers']['Do you have 2 or more keys or keyless remotes?'] == 'Yes',
                                'type': 'Boolean',
                            }
                        ],
                    },
                    {
                        'canonicalName': 'other',
                        'answers': [
                            {
                                'questionId': 'qx/IncomingURL',
                                'value': 'https://www.kbb.com/instant-cash-offer/',
                            },
                            {
                                'questionId': 'qx/BrowserType',
                                'value': self.settings['USER_AGENT'],
                            },
                            {
                                'questionId': 'qx/HttpReferer',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/AutotraderCarID',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/LandingPage',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/Asset',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/LnxCode',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/ExpCode',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/ReturnerID',
                                'value': '',
                            },
                            {
                                'questionId':'qx/ExtRefID',
                                'value':''
                            },
                            {
                                'questionId': 'qx/SiteReferralUserID',
                                'value': '00000000-0000-0000-0000-000000000000',
                            },
                            {
                                'questionId': 'qx/ConsumerGenerated',
                                'value': True,
                            },
                            {
                                'questionId': 'qx/OfferCode',
                                'value': 'B',
                            },
                            {
                                'questionId': 'qx/UserComments',
                            },
                            {
                                'questionId': 'qx/ConsumerCommunicationMethod',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/PixAllID',
                                'value': '',
                                # 'value': '8KvQCH2Eqp6iUIucd2all8Ex',
                            },
                            {
                                'questionId': 'qx/PixAllRealID',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/AuctionQuestionAnsweredByUser',
                                'value': '',
                            },
                            {
                                'questionId': 'qx/AreQuestionsVerified',
                                'value': 1,
                            },
                            {
                                'questionId': 'qx/VerifiedMileage',
                                'value': autocheck_data['miles'],
                            },
                            {
                                'questionId': 'qx/AnswerSourcesInput',
                                'value': [{
                                    'questionCode': 'DealerModifiedAccidentQuestion',
                                    'value': False,
                                }],
                            },
                            {
                                'questionId': 'qx/IPAddress',
                                'value': public_ip_address,
                            },
                        ],
                    },
                    {
                        'canonicalName': 'conditions',
                        'answers': [self.condition_codes[part_condition] for part_condition in self.site_conditions[condition] if self.condition_codes[part_condition]['questionId'] in prospect_questions],
                    },
                    {
                        'canonicalName': 'contactInfo',
                        'answers': {
                            'firstName': result['first_name'],
                            'lastName': result['last_name'],
                            'zip': result['zip_code'],
                            'email': result['email'],
                            'confirmEmail': result['email'],
                            'phone': result['phone_number'],
                            'legalAcceptance': True,
                        },
                    },
                    {
                        'canonicalName': 'replacementVehicle',
                        'answers': [{
                            'questionId': 'qrv/LeadType',
                            'value': 'CashOffer',
                        }],
                    },
                ],
            },
        )

        offer_response = yield scrapy.Request(
            method='POST',
            url=f'https://api.kbb.com/ico/v1/offers/?prospectId={prospect_id}&api_key={self.api_key}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'text/json',
                'Referer': 'https://www.kbb.com/instant-cash-offer/',
                'QuestionConversion': 'fury',
                # 'TraceId': '65ab7999-b69f-45d8-a4b0-ca5dc06339b9',
            },
            body=' '.encode(),
        )

        offer = offer_response.json()

        if 400080 in offer['meta']['codes']:
            self.logger.error('Please enter a valid first name.')
            raise InvalidContactInfo()

        elif 400081 in offer['meta']['codes']:
            self.logger.error('Please enter a valid last name.')
            raise InvalidContactInfo()

        elif 400082 in offer['meta']['codes']:
            self.logger.error('Please enter a valid e-mail address.')
            raise InvalidContactInfo()

        elif 400084 in offer['meta']['codes']:
            self.logger.error('Please enter a valid phone number.')
            raise InvalidContactInfo()

        elif 400094 in offer['meta']['codes']:
            self.logger.error('It looks like you\'ve tried to create several different Instant Cash Offers (This is most likely them detecting that the e-mail is a wildcard/invalid e-mail).')
            raise InvalidContactInfo()

        elif 400095 in offer['meta']['codes']:
            self.logger.error(
                'There is already an offer for this vehicle. Please contact the dealer to make any needed changes.')
            result['success'] = 'Already an active offer'

        elif 400097 in offer['meta']['codes']:
            self.logger.error('There are multiple ICO offers based on the information provided.')
            raise ContactInfoInUse()

        elif offer['data']['status'] == 'CLEARED':
            price = float(offer['data']['amount'])

            result['price'] = price

        elif offer['data']['status'] == 'INSPECTION':
            result['success'] = 'Sorry, your vehicle doesn\'t qualify for an Instant Cash Offer'

        elif offer['data']['status'] == 'FR':
            self.logger.error('A Kelley Blue Book representative is still reviewing your information. We\'ll send you an email when we have an update.')
            raise OfferUnderReview

        elif offer['data']['status'] == 'INELIGIBLE':
            result['success'] = 'This vehicle isn\'t eligible for an Instant Cash Offer.'

        else:
            result['success'] = 'Sorry, your vehicle doesn\'t qualify for an Instant Cash Offer'

        yield result
