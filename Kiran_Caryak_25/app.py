from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import Any
import sys
import json
import math
import random


def load_json():
    with open('vins.json', 'r') as file:
        return json.load(file)


def string_to_float_if_possible(val: str):
    try:
        return float(val)

    except ValueError:
        return val


def parse_arguments(args) -> dict[str, Any]:
    return {k: string_to_float_if_possible(v) for k, v in (arg.split('=', 1) for arg in args)}


def main(config_file: str, site_names: str, condition: str, **kwargs):
    vin_info = load_json()[int(kwargs['vin_index'])] if 'vin_index' in kwargs else {
        'vin_number': kwargs['vin_number'], 'mileage': kwargs['mileage']}

    test_vin = vin_info['vin_number']
    mileage = math.ceil((vin_info['mileage'] + 1001) / 1000) * 1000

    process = CrawlerProcess(get_project_settings())

    for site_name in site_names.split(','):
        first_name = 'Jaina'
        last_name = 'Williams'
        random_id = random.randrange(1_000_000)
        random_phone_number = '2052030652'
        random_zipcode = '84020'

        process.crawl(f'car_prices_{site_name}', config_file=config_file, debug_mode=True, first_name=first_name, last_name=last_name, email=f'{first_name}.{last_name}{random_id}@gmail.com'.lower(
        ), phone_number=random_phone_number, vin=test_vin, trim='neep', zip_code=random_zipcode, mileage=mileage, condition=condition, batch_id='-1', batch_com='-1')

    process.start()


if __name__ == '__main__':
    main(**parse_arguments(sys.argv[1:]))
