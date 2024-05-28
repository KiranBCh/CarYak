from datetime import datetime
import scrapy
import scrapy.http
from uuid import uuid4
from car_prices.exceptions import CantMakeOfferForVin
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesEdmundsSpider(car_prices_spider(source='Edmunds')):
    site_conditions = {
        'bad': 'Rough',
        'moderate': 'Average',
        'good': 'Clean',
        'excellent': 'Outstanding',
    }

    condition_codes = {
        'bad': 'Rough',
        'moderate': 'Average',
        'good': 'Clean',
        'excellent': 'Outstanding',
    }

    def answers_to_offer_questions(self, condition):
        return {
            'Vehicle Condition': self.site_conditions[condition],
            'Has the vehicle ever been in an accident?': 'No',
            'Does the vehicle have any frame damage?': 'No',
            'Does the vehicle have any flood damage?': 'No',
            'Has this vehicle been smoked in?': 'No',
            'Are any interior parts broken or inoperable?': 'No',
            'Are there any rips, tears, or stains in the interior?': 'No',
            'Are there any mechanical issues or warning lights displayed on the dashboard?': 'No',
            'Has the odometer ever been broken or replaced?': 'No',
            'Are there any panels in need of paint or body work?': 'No',
            'Any major rust and/or hail damage?': 'No',
            'Do any tires need to be replaced?': 'No',
            'How many keys do you have?': '2 or more',
            'Does the vehicle have any aftermarket modifications?': 'No',
            'Are there any other issues with the vehicle?': 'No',
            'Title Status': 'Clean',
            'Is the vehicle owned outright?': 'Yes',
            'Is the title in the seller\'s possession?': 'Yes',
            'Are there any visible defects?': 'No',
            'Does the windshield need to be replaced?': 'No',
            'Has there ever been any fire damage?': 'No',
            'What is the seat material?': 'Cloth',
            'Are there any other adverse smells?': 'No',
            'Does the vehicle drive?': 'Yes',
            'Is any standard maintenance needed?': 'No',
            'Are there any fluid leaks?': 'No',
            'Are any mechanical repairs needed?': 'No',
            'How many miles are on the tires?': 'Under 10,000',
            'Is there any wheel damage?': 'No',
            'Does the vehicle have key fobs?': 'No',
        }

    def process_requests(self, result):
        condition = result['condition']
        result['answers'] = self.answers_to_offer_questions(condition)

        vin_details_response = yield scrapy.Request(
            method='GET',
            url=f'https://www.edmunds.com/gateway/api/vehicle/v3/styles/vins/{result["vin_number"]}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.edmunds.com/appraisal/",
                # "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMwODYwNjUiLCJhcCI6IjQ1NTk0OTUyNSIsImlkIjoiODU4YjEwN2M5ZjQ1YzdlZSIsInRyIjoiZjFiYzlhMmVmNzM3MTAyYTQyOGFiODYyOTMxNGJmMTAiLCJ0aSI6MTY4MTA5ODQwMjA1NX19",
                # "traceparent": "00-f1bc9a2ef737102a428ab8629314bf10-858b107c9f45c7ee-01",
                # "tracestate": "3086065@nr=0-1-3086065-455949525-858b107c9f45c7ee----1681098402055",
                # "x-deadline": "1681098402553",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1NNN; location=j%3A%7B%22zipCode%22%3A%2230033%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22404%2F470%2F678%2F770%22%2C%22timeZone%22%3A%22Eastern%22%2C%22gmtOffset%22%3A-5%2C%22dst%22%3A%221%22%2C%22latitude%22%3A33.817078%2C%22longitude%22%3A-84.281903%2C%22salesTax%22%3A0.066%2C%22dma%22%3A%22524%22%2C%22dmaRank%22%3A6%2C%22stateCode%22%3A%22GA%22%2C%22city%22%3A%22Decatur%22%2C%22county%22%3A%22DeKalb%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Georgia%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22ipZipCode%22%3A%2230033%22%2C%22userIP%22%3A%22216.98.233.50%22%2C%22userSet%22%3Anull%7D; EdmundsYear=\"&zip=30033&dma=524:IP&city=Decatur&state=GA&lat=33.817078&lon=-84.281903\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaMP9PlyHAQAAfrhFaRP4lO38M5+QkC79D9qKTiRKOPjs2EudSON9OEnNDZclb/aFXKm4zLjPUxVzwZpKwXiTt6WIv0pCzcsC2+JNN80C6gHka3a0ygl45dUgy3DJOn2XB5qMl5RNAgE5XifDk7tPEf61oG3GtVqKUKAZ0WTg2lrzf8EEX78ECuATU8rlxdely0HKIPgI/mFe7clGf/mkSsbtDCjcHa7cIQaNRk5ZmALOHVFq7QamzXvPow==~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.0.1681098391.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
        )
        if not vin_details_response.json():
            self.logger.error('We could not locate this VIN. Please confirm you entered the VIN correctly.')
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)
        
        vehicle_candidates = [
            item for item in vin_details_response.json() if item['year'] == result['year']]
        vehicle_candidates.sort(reverse=True, key=lambda vehicle_item: self.vehicle_aspect_match_score(' '.join(
            [vehicle_item['makeName'], vehicle_item['modelName'], vehicle_item['styleName']]), result['kbb_details']['vehicle_name']))

        vehicle_info = vehicle_candidates[0]
        raw_make = vehicle_info['makeName']
        raw_model = vehicle_info['modelName']
        make = raw_make.lower().replace(' ', '-')
        model = raw_model.lower().replace(' ', '-')
        year = vehicle_info['year']
        style_id = vehicle_info['styleId']

        style_details_response = yield scrapy.FormRequest(
            method='GET',
            url=f'https://www.edmunds.com/gateway/graphql/federation/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "content-type": "application/json",
                # "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMwODYwNjUiLCJhcCI6IjQ1NTk0OTUyNSIsImlkIjoiNDM1MjM0OTZjZDhkNTBmYSIsInRyIjoiMjgxNWMxNTVlMDA0OGE2NTA2MjE4NDZmMGIxN2U0ZjAiLCJ0aSI6MTY4MTA5ODQwNjEyMH19",
                # "traceparent": "00-2815c155e0048a650621846f0b17e4f0-43523496cd8d50fa-01",
                # "tracestate": "3086065@nr=0-1-3086065-455949525-43523496cd8d50fa----1681098406120",
                "x-artifact-id": "venom",
                "x-artifact-version": "2.0.3884",
                "x-client-action-name": "used_model_mydp_tmv_appraiser_style.styles.optionsWithOemCodes",
                "x-edw-page-cat": "used_model_mydp",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-trace-seq": "2",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2230033%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22404%2F470%2F678%2F770%22%2C%22timeZone%22%3A%22Eastern%22%2C%22gmtOffset%22%3A-5%2C%22dst%22%3A%221%22%2C%22latitude%22%3A33.817078%2C%22longitude%22%3A-84.281903%2C%22salesTax%22%3A0.066%2C%22dma%22%3A%22524%22%2C%22dmaRank%22%3A6%2C%22stateCode%22%3A%22GA%22%2C%22city%22%3A%22Decatur%22%2C%22county%22%3A%22DeKalb%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Georgia%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22ipZipCode%22%3A%2230033%22%2C%22userIP%22%3A%22216.98.233.50%22%2C%22userSet%22%3Anull%7D; EdmundsYear=\"&zip=30033&dma=524:IP&city=Decatur&state=GA&lat=33.817078&lon=-84.281903\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaHgAP1yHAQAAe+9FaRMCkQG4dPXiXUIsCDlLMXKz8gJjqV1wCaE1GalCHiJZf7o1uY6npf1M5nAyHaCQtjAjgXnqG2tE6h1f2eDUwKFZLrQeWMYjkZBzh9tjdoj3x6mLiVjeyzOpNJhJ/zduKAscv5E9+q04NPaLO/8Urb9t0bbrwtdZNg2eR0wx9eOThxCT1ZZFQIajTILhTdk6yeHypJfmGJ21bSGlLO8M1vxFnqiyaQMzxxRwbRmryQ==~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098403.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'variables': f'{{"styleId":"{style_id}"}}',
                #'extensions': f'{{"persistedQuery":{{"version":1,"sha256Hash":"3469aaf49a750cd3a0f57d9987375e6755bf60539d40dd595608f2e3a8e6ef86"}}}}',
                'extensions': f'{{"persistedQuery":{{"version":1,"sha256Hash":"14ff49b9606272d4f6806a0033afa4e04b72e3f4b93676d84f517a7285c32fec"}}}}',
            },
        )

        style_details = style_details_response.json()

        drivetrain = style_details['data']['style']['driveTrain']
        transmission = style_details['data']['style']['transmission']['transmissionType']
        engine_size = style_details['data']['style']['engine']['size']
        chrome_style_ids = style_details['data']['style']['partnerMapping']['chromeIds']

        estimates_response = yield scrapy.FormRequest(
            method='GET',
            url='https://www.edmunds.com/gateway/api/v2/usedtmv/getalltmvbands',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "x-artifact-id": "venom",
                "x-client-action-name": "used_model_mydp_tmv_appraiser_style.styles.pricing.usedTmv.withOptions",
                "x-artifact-version": "2.0.3884",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-edw-page-cat": "used_model_mydp",
                "x-trace-seq": "2",
                "x-referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/",
                # "x-deadline": "1681098494217",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2277381%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22713%2F281%2F832%22%2C%22timeZone%22%3A%22Central%22%2C%22gmtOffset%22%3A-6%2C%22dst%22%3A%221%22%2C%22latitude%22%3A30.16848%2C%22longitude%22%3A-95.48964%2C%22salesTax%22%3A0.0625%2C%22dma%22%3A%22618%22%2C%22dmaRank%22%3A7%2C%22stateCode%22%3A%22TX%22%2C%22city%22%3A%22Spring%22%2C%22county%22%3A%22Montgomery%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Texas%22%2C%22userSet%22%3Atrue%2C%22ipZipCode%22%3A%2230033%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22userIP%22%3A%22216.98.233.50%22%7D; EdmundsYear=\"&zip=77381&dma=618:ZIP&city=Spring&state=TX&lat=30.16848&lon=-95.48964&userSet=false\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaI8PP1yHAQAAHidHaRMnsRtv15sWIOfbk/jtbBBYskFPFV+JHNiKMg4wHcu5BKpowDWuZDsoYMNbF4N3vVhG+wdCMp5L+qoTBB/yX+nQuuYktPO5JQao2eNUCf0DWdVXxILQ9BFjQ0RpiKO6Whar0Nr6rObQKyNba/GYxpT06gU/dak+iKxB8ViucTRDH7f6nPpZXPRaiM7ixU5WhAcjnX20K/G1XOFa9qjggBZqF9/cVyg8tPz05mGdUIA=~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098487.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'styleid': str(style_id),
                'zipcode': result['zip_code'],
                'mileage': str(result['mileage']),
                # 'colorid': str(200072360),
                'typical': 'false',
                'view': 'full',
                'priceband': 'false',
            },
        )

        estimates = estimates_response.json()

        outstanding_estimate = str(
            estimates['tmvconditions']['OUTSTANDING']['Current']['totalWithOptions']['usedTradeIn'])
        clean_estimate = str(
            estimates['tmvconditions']['CLEAN']['Current']['totalWithOptions']['usedTradeIn'])
        average_estimate = str(
            estimates['tmvconditions']['AVERAGE']['Current']['totalWithOptions']['usedTradeIn'])
        rough_estimate = str(
            estimates['tmvconditions']['ROUGH']['Current']['totalWithOptions']['usedTradeIn'])

        style_code_response = yield scrapy.FormRequest(
            method='GET',
            url='https://www.edmunds.com/api/partner-offers/v2/translation/chrome-style',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "content-type": "application/json",
                "X-Product-Id": "venom",
                "x-artifact-id": "venom",
                "x-client-action-name": "used_model_mydp_tmv_appraiser_style.styleId.chromeStyleIds.engineSize.transmissionType.vin.skuAndOptions",
                "x-artifact-version": "2.0.3884",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-edw-page-cat": "used_model_mydp",
                "x-trace-seq": "2",
                "x-referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2277381%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22713%2F281%2F832%22%2C%22timeZone%22%3A%22Central%22%2C%22gmtOffset%22%3A-6%2C%22dst%22%3A%221%22%2C%22latitude%22%3A30.16848%2C%22longitude%22%3A-95.48964%2C%22salesTax%22%3A0.0625%2C%22dma%22%3A%22618%22%2C%22dmaRank%22%3A7%2C%22stateCode%22%3A%22TX%22%2C%22city%22%3A%22Spring%22%2C%22county%22%3A%22Montgomery%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Texas%22%2C%22userSet%22%3Atrue%2C%22ipZipCode%22%3A%2230033%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22userIP%22%3A%22216.98.233.50%22%7D; EdmundsYear=\"&zip=77381&dma=618:ZIP&city=Spring&state=TX&lat=30.16848&lon=-95.48964&userSet=false\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaKMSP1yHAQAAOGNHaRMRObPNwANEVwuXSmUl/+T13Ay7YbX/R7n4mbw9LGAlDBJjx/KemWB8GupEBY3yytUIvZK8Z7E91oANqXeDdVvQ/PhR32Qpk4N7cOULPEPCzyVnKpvcCeymu2adOFOQ3DHHfTmrRCJis/RutOqMSxZjX6fv92Qgz7AGM0jT51NbPRhBuPH9riFAUrVVXOBI7KsQO5I/INhMbFuomUrWTRMk+21a3Bk1/3kx84ksmeI=~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098487.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'EngineSize': str(engine_size),
                'TransmissionType': transmission,
                'Metadata[EdmundsStyleId]': str(style_id),
                'Metadata[Vin]': result['vin_number'],
            } | ({
                'ChromeStyleId': chrome_style_ids[0],
            } if chrome_style_ids else {}),
        )
        try:style_code = style_code_response.json()['sku']
        except:
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)
        
        equipment_options_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.edmunds.com/api/partner-offers/v2/translation/equipment-options',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "content-type": "application/json",
                "X-Product-Id": "venom",
                "x-artifact-id": "venom",
                "x-client-action-name": "used_model_mydp_tmv_appraiser_style.styleId.chromeStyleIds.engineSize.transmissionType.vin.skuAndOptions",
                "x-artifact-version": "2.0.3884",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-edw-page-cat": "used_model_mydp",
                "x-trace-seq": "2",
                "x-referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/",
                "Origin": "https://www.edmunds.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2277381%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22713%2F281%2F832%22%2C%22timeZone%22%3A%22Central%22%2C%22gmtOffset%22%3A-6%2C%22dst%22%3A%221%22%2C%22latitude%22%3A30.16848%2C%22longitude%22%3A-95.48964%2C%22salesTax%22%3A0.0625%2C%22dma%22%3A%22618%22%2C%22dmaRank%22%3A7%2C%22stateCode%22%3A%22TX%22%2C%22city%22%3A%22Spring%22%2C%22county%22%3A%22Montgomery%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Texas%22%2C%22userSet%22%3Atrue%2C%22ipZipCode%22%3A%2230033%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22userIP%22%3A%22216.98.233.50%22%7D; EdmundsYear=\"&zip=77381&dma=618:ZIP&city=Spring&state=TX&lat=30.16848&lon=-95.48964&userSet=false\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaOESP1yHAQAAcGZHaRNHI1xtrWBQqM+810x7dAFkNBU4BR06YaAGKTLvhPdLISnLInNeJvRnrJWgjXo9xZ0zTbkbyhPOdPRhydlbvmRRkGUR4+NuAmsxrTwzYO1zUU6fpux/ElAi1S51DWKDtj9HnlBn40sw842fpyXRXCoTpHyQ3k2UqNNGmMwvnwUfdMHhwOBBuJudAxMAnpA2MN+Z4wppoeS/MVzXY+UnToFzexWVEzEwwpeFaHZjI9o=~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098487.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "sku": style_code,
                "partnerEquipmentDescriptions": [],
                "manufacturerOptionCodes": []
            },
        )

        equipment_options = equipment_options_response.json()
        available_option_codes = equipment_options['availableOptionCodes']
        standard_option_codes = equipment_options['standardOptionCodes']

        if not standard_option_codes:
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)

        quote_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.edmunds.com/api/partner-offers/v2/quotes',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "content-type": "application/json",
                "X-Product-Id": "venom",
                "x-artifact-id": "venom",
                "x-client-action-name": "used_model_mydp_tmv_appraiser_style.vin.make.model.year.eligibility",
                "x-artifact-version": "2.0.3884",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-edw-page-cat": "used_model_mydp",
                "x-trace-seq": "2",
                "x-referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/",
                "Origin": "https://www.edmunds.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2277381%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22713%2F281%2F832%22%2C%22timeZone%22%3A%22Central%22%2C%22gmtOffset%22%3A-6%2C%22dst%22%3A%221%22%2C%22latitude%22%3A30.16848%2C%22longitude%22%3A-95.48964%2C%22salesTax%22%3A0.0625%2C%22dma%22%3A%22618%22%2C%22dmaRank%22%3A7%2C%22stateCode%22%3A%22TX%22%2C%22city%22%3A%22Spring%22%2C%22county%22%3A%22Montgomery%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Texas%22%2C%22userSet%22%3Atrue%2C%22ipZipCode%22%3A%2230033%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22userIP%22%3A%22216.98.233.50%22%7D; EdmundsYear=\"&zip=77381&dma=618:ZIP&city=Spring&state=TX&lat=30.16848&lon=-95.48964&userSet=false\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaAETP1yHAQAAIGlHaRODcCgSds7Sbn0NkK/1al24BVSQo1IK9KMP+EWh+Ug7bNkO4z4lbv4OFIT1OlGErmtO4ZQ7qf8rVAtUYs+mGKR5qWSxnGwCWiYJ4tDeZXbO2O7lV3Blc/bgkX9m8o6sciiWhRRX2vfx6UQzMoK2XKUNZ1dRFvd6ErWALZHIHS/MiMngmUfh3ZMSMLxKFudkUXXeeFUbubkvKOJ0Wa12bSutltdrE4uTUv36mDzW7bI=~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098487.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "vin": result['vin_number']
            },
        )

        quote = quote_response.json()
        quote_id = quote['id']
        if not quote['isEligible'] and not quote['lastQuote']:	
            raise CantMakeOfferForVin(needs_to_see_vehicle=True)
        elif not quote['isEligible']:
            # result['success'] = f'We were unable to find a local offer for your {year} {raw_make} {raw_model}'
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)

        source_uuid = str(uuid4())

        submission_time = datetime.utcnow().isoformat()[:23] + 'Z'

        offer_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://www.edmunds.com/api/partner-offers/v2/quotes/{quote_id}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.edmunds.com/{make}/{model}/{year}/appraisal-value/?vin={result['vin_number']}&styleIds={style_id}",
                "x-edw-page-name": "used_model_mydp_tmv_appraiser_style",
                "x-edw-page-cat": "used_model_mydp",
                # "x-trace-id": "Root=1-643386a3-64a0a405094703d104eed080",
                "x-artifact-version": "2.0.3884",
                "x-artifact-id": "venom",
                "content-type": "application/json",
                "X-Product-Id": "venom",
                "Origin": "https://www.edmunds.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "feature-flags=j%3A%7B%7D; visitor-id=5df4c363-85f0-442f-b362-12bbae1aa50d; edmunds=5df4c363-85f0-442f-b362-12bbae1aa50d; session-id=155030495478478620; edw=155030495478478620; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2277381%22%2C%22type%22%3A%22Standard%22%2C%22areaCode%22%3A%22713%2F281%2F832%22%2C%22timeZone%22%3A%22Central%22%2C%22gmtOffset%22%3A-6%2C%22dst%22%3A%221%22%2C%22latitude%22%3A30.16848%2C%22longitude%22%3A-95.48964%2C%22salesTax%22%3A0.0625%2C%22dma%22%3A%22618%22%2C%22dmaRank%22%3A7%2C%22stateCode%22%3A%22TX%22%2C%22city%22%3A%22Spring%22%2C%22county%22%3A%22Montgomery%22%2C%22inPilotDMA%22%3Atrue%2C%22state%22%3A%22Texas%22%2C%22userSet%22%3Atrue%2C%22ipZipCode%22%3A%2230033%22%2C%22ipDma%22%3A%22524%22%2C%22ipStateCode%22%3A%22GA%22%2C%22userIP%22%3A%22216.98.233.50%22%7D; EdmundsYear=\"&zip=77381&dma=618:ZIP&city=Spring&state=TX&lat=30.16848&lon=-95.48964&userSet=false\"; entry_url=www.edmunds.com%2Fappraisal%2F; entry_page=used_cars_tmv_appraiser; entry_url_params=%7B%7D; device-characterization=false,false; content-targeting=US,WA,SEATTLE,819,-122.3343,47.6115,98101-98109+98111-98112+98114-98119+98121-98122+98124-98126+98129+98131-98134+98136+98138+98144-98146+98148+98154-98155+98158+98160-98161+98164+98166+98168+98170+98174+98177-98178+98181+98185+98188-98191+98195+98198-98199; ak_bmsc=EA90231F29071863C254EF2031FE3B9A~000000000000000000000000000000~YAAQ0M9YaNP8PlyHAQAApKpFaRNz8y4tLBKIFgd2Ohq1qEa3eQyXTq7OCDAbylW+4mjFRY25yEMxPoY9Rlm6qU/vBH4C50/ie2mqfLOrUIts1JRqRcjWEuEgFFMS5u44lSzHDyXVCcVgFOdufyogB8ZW+6LELGdz50Dfw+70Ul2QrHkoCHiUdgSTTY4HQR/Uiklke2fongZWA0xm0GG32PXU8Q2vRcL2NqrR2Hfd9XEWBXukmCT6YqPyMP2LdnfGJGp1RA23Sa1WViHGG1BI+YdTEk05y/sLANbwFFbCClhOpBVKCvEGjn92ihhXo29xIhz5v38gpm78dcQjbBVs1fzVM2GdcfsNj3rcAf3uTxMZBY2T86Kgp9VaIu2bxYG4w3xjxxchTos=; lux_uid=168109838908150137; bm_sv=E4C9D80F97BCA9960AD613B30D3DAD4B~YAAQ0M9YaEgTP1yHAQAA9W9HaROQdrdbLdt3/D7JZuMiP5a6iUaEDQt5KMHMVZ+wQ/oNegvBEWG9uw/au19H2NFYfFDbjGvzcsCNfpBMHi2u0OIDvA3+L0jcLHN5+PNjYho4v5Xsaow3dHzfyv1pgdc1CuW9xfueqfVCcNuIJMDkKmGcWO8jlTpKEg435ujjdham5tGYqCnxam5WfXGItETshSLyGOQ6Cxe3Q3FohYdYhJ6bafpwLSIOLrvThUt2VQw=~1; _ga_Z1SEPKTH2P=GS1.1.1681098391.1.1.1681098487.0.0.0; _ga=GA1.1.1759473457.1681098392; _uetsid=49e36640d75211edb0b4231aeebc934a; _uetvid=49e36070d75211ed98a36989cbd91969",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "styleCode": style_code,
                "vin": result['vin_number'],
                "sourceId": source_uuid,  # "7c144711-89d9-5aff-a0d8-9eef701675e2",
                "createdDateUtc": submission_time,
                "mileage": result['mileage'],
                "zipCode": result['zip_code'],
                "transmission": transmission,
                # "exteriorColorCode": 99,
                "conditionQuestions": [
                    {
                        "id": 300,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 410,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 420,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 500,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 600,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 830,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 910,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 920,
                        "answers": [
                            1
                        ]
                    },
                    {
                        "id": 1000,
                        "answers": [
                            1
                        ]
                    }
                ],
                "visitorId": None,
                "ciamId": None,
                "drive": drivetrain,
                "availableOptions": available_option_codes,
                "standardOptions": standard_option_codes,
                "metadata": {
                    # "interior_color": "Graphite",
                    "edmunds_style_id": str(style_id),
                    "sem_campaign": "false",
                    "remote_host_request_id": "EVAL-1950",
                    "remote_host_client_id": "",
                    "edmunds-Condition-Input": self.condition_codes[result['condition']],
                    "edmunds_make_name": raw_make,
                    "edmunds_model_name": raw_model,
                    "edmunds_year": str(year),
                    "edmunds-Outstanding": str(outstanding_estimate),
                    "edmunds-Final-TMV-Value": str(outstanding_estimate),
                    "edmunds-Clean": str(clean_estimate),
                    "edmunds-Average": str(average_estimate),
                    "edmunds-Rough": str(rough_estimate)
                }
            },
        )

        offer = offer_response.json()
        decline_reason = offer['declineReason']
        decline_reason_message = ['offer_exceeds_upper_limit',
                'not_in_mmy_white_list', 'mpy_outside_guardrails']
        
        if offer['declineReason'] == "" and offer['valuation'] != 0:
            result['price'] = offer['valuation']

        elif 'found in blacklist' in decline_reason:
            result['success'] = 'No offer'

        #elif offer['declineReason'] in decline_reason_message:
        #    result['success'] = 'No offer'
        else:
            result['success'] = 'Needs to see vehicle'

        yield result
