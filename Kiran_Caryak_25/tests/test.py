import sys
import time
from unittest import TestCase
from car_prices.config import Config
import subprocess
import car_prices.mongodb as mongodb
import requests
from signal import SIGINT
from typing import cast
import concurrent.futures


config_file = 'config/scrabing_engine_config.toml'


class TestCarYak(TestCase):
    sites = ['allcars', 'cargurus', 'carmax', 'cars', 'carvana', 'driveway', 'edmunds', 'kbb', 'kbb_ico', 'peddle', 'sellmax', 'truecar', 'vroom']

    configs = {site: Config(config_file, site) for site in sites}

    @classmethod
    def setUpClass(cls) -> None:
        cls.service_process = subprocess.Popen([sys.executable, 'services.py'])

        cls.databases = {site: mongodb.Database(config.database) for site, config in cls.configs.items()}

        # Wait for it to start
        time.sleep(60)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.service_process.send_signal(SIGINT)
        # cls.service_process.terminate()
        cls.service_process.communicate()

    def offers_work(self, site_name: str, batch_id: int):
        return requests.post(
            url='http://localhost:14200/schedule.json',
            data={
                'project': 'caryak',
                'spider': f'car_prices_{site_name}',
                'testing': 'true',
                'batch_id': str(batch_id),
                'batch_com': str(batch_id),
                'vin': '5YJ3E1EB7MF960910',
                'trim': '""',
                'zip_code': '77381',
                'mileage': '81000',
                'condition': 'excellent',
            }
        ).json()

    def vin_details_work(self, _: str, batch_id: int):
        return requests.post(
            url='http://localhost:14200/schedule.json',
            data={
                'project': 'caryak',
                'spider': 'vin_details_kbb',
                'testing': 'true',
                'batch_id': str(batch_id),
                'batch_com': str(batch_id),
                'vin': '5YJ3E1EB7MF960910',
            }
        ).json()

    def test_database_result(self) -> None:
        self.maxDiff = None
        works = {'cars': self.offers_work, 'vin_details': self.vin_details_work}

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.sites) * len(works)) as executor:
            # Start the works first.
            highest_wait = max(self.configs[site_name].engine.timeout_in_seconds for site_name in self.sites)

            def create_job(batch_id, work_name, work, site_name):
                database = self.databases[site_name]

                database.handle[f'{work_name}_test'].delete_many({'batch_id': batch_id})
                database.handle['logs_test'].delete_many({'batch_id': batch_id})

                return executor.submit(work, site_name, batch_id)

            job_details = [(-1 - index, work_name, work, site_name)
                           for (index, (work_name, work, site_name))
                           in enumerate((work_name, work, site_name) for work_name, work in works.items() for site_name in self.sites)]
            job_to_details_map = {create_job(batch_id, work_name, work, site_name): (batch_id, work_name, site_name) for batch_id, work_name, work, site_name in job_details}

            for job in concurrent.futures.as_completed(job_to_details_map, highest_wait * 1.2):
                batch_id, work_name, site_name = job_to_details_map[job]
                with self.subTest(work_name=work_name, site_name=site_name):
                    database = self.databases[site_name]

                    document = database.handle[f'{work_name}_test'].find_one({'batch_id': batch_id})
                    log = database.handle['logs_test'].find_one({'batch_id': batch_id})

                    result = job.result()

                    self.assertIsNotNone(document)
                    self.assertIsNotNone(log)

                    self.assertEqual(cast(dict, document)['success'], result['result']['success'])

                    if 'price' in cast(dict, document):
                        self.assertEqual(cast(dict, document)['price'], result['result']['price'])

                    self.assertEqual(cast(dict, log)['text'], result['log'])

                    database.handle[f'{work_name}_test'].delete_many({'batch_id': batch_id})
                    database.handle['logs_test'].delete_many({'batch_id': batch_id})
