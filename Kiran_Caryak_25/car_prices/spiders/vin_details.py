import scrapy
from car_prices.spiders.basic import Result, basic_spider


def vin_details_spider(source: str):
    class Spider(basic_spider(source=source, category='vin_details')):
        allowed_domains = [
            'carfax.com',
            'carsforsale.com',
            'herbchambers.com',
            'ksl.com',
            'azcarcentral.com',
            'webuyanycarusa.com',
        ]

        def __init__(self, batch_com: str, batch_id: str, vin: str, *args, **kwargs):
            super().__init__(batch_com=batch_com, batch_id=batch_id, *args, **kwargs)

            self.vin = vin.upper()

        def get_additional_result_details(self) -> Result:
            return {
                'vin_number': self.vin,
                'batch_id': self.batch_id,
                'batch_com': self.batch_com,
            }

    return Spider


class VinDetailsKbbSpider(vin_details_spider(source='KBB')):
    allowed_domains = [
        'carfax.com',
        'carsforsale.com',
        'herbchambers.com',
        'ksl.com',
        'azcarcentral.com',
        'webuyanycarusa.com',
    ]

    def process_requests(self, result):
        details_response = yield scrapy.FormRequest(
                method='GET',
                url=f'https://api.kbb.com/ico/v1/vehicles/vin/{result["vin_number"]}/',
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-GB,en;q=0.9",
                    "content-type": "text/json",
                    "origin": "https://www.kbb.com",
                    "questionconversion": "fury",
                    "referer": "https://www.kbb.com/",
                    # "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                    # "sec-ch-ua-mobile": "?0",
                    # "sec-ch-ua-platform": "\"Linux\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    # "traceid": "9a7286fd-9764-431c-b5b0-4c16f6c6dcf0",
                    # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                },
                formdata={
                    "cadsBypass": "false",
                    "vinVerified": "true",
                    "fromAuction": "undefined",
                    "api_key": "kehj9w5vxkt4t8yugn5zkpey"
                },
            )

        details = details_response.json()['data']['possibilities'][0]

        year = int(details['year']['displayName'])
        make = details['make']['displayName']
        model = details['model']['displayName']
        trim = details['trim']['displayName']
        colours = [item['displayName'] for item in details['colors']]
        engine_options = [item['displayName'] for item in details['engines']]
        transmission_options = [item['displayName']
                                for item in details['transmissions']]
        drivetrain_options = [item['displayName']
                              for item in details['drivetrains']]

        result['year'] = year
        result['make'] = make
        result['model'] = model
        result['trims'] = [{
            'name': trim,
            'colours': colours,
            'engine_options': engine_options,
            'transmission_options': transmission_options,
            'drivetrain_options': drivetrain_options,
        }]

        yield result
