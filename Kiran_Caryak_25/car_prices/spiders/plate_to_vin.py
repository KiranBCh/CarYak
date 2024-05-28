import scrapy
from car_prices.spiders.basic import Result, basic_spider


def plate_to_vin_spider(source: str):
    class Spider(basic_spider(source=source, category='plate_to_vin')):
        def __init__(self, batch_com: str, batch_id: str, state_code: str, plate_number: str, *args, **kwargs):
            super().__init__(batch_com=batch_com, batch_id=batch_id, *args, **kwargs)

            self.state_code = state_code
            self.plate_number = plate_number

        def get_additional_result_details(self) -> Result:
            return {
                'state_code': self.state_code,
                'plate_number': self.plate_number,
            }

    return Spider


class PlateToVinKbbSpider(plate_to_vin_spider(source='KBB')):
    api_key = 'kehj9w5vxkt4t8yugn5zkpey'

    def process_requests(self, result):
        plate_to_vin_response = yield scrapy.FormRequest(
            method='GET',
            url='https://api.kbb.com/ico/v1/plate2vin/lookup',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.kbb.com/",
                "QuestionConversion": "fury",
                # "TraceId": "1ad40f90-e722-459b-b420-bdb68d543d77",
                "Content-Type": "text/json",
                "Origin": "https://www.kbb.com",
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
                'stateCode': self.state_code.upper(),
                'plateNumber': self.plate_number.upper(),
                'api_key': self.api_key,
            },
        )

        possible_vins = plate_to_vin_response.json()['data']['vins']

        if len(possible_vins) > 0:
            result['vin_number'] = possible_vins[0]['vin']
        else:
            result['success'] = 'Vin not found'

        yield result
