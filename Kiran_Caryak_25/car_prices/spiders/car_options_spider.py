import scrapy
import scrapy.http
import re


class CarPricesSpider(scrapy.Spider):
    name = 'car_options'
    collection_name = 'options'

    allowed_domains = [
        'www.kbb.com',
    ]

    special_character_except_dash_and_underscore_pattern = re.compile(
        r'[^a-zA-Z0-9_-]')

    def start_requests(self):
        result = {}

        yield scrapy.http.JsonRequest(
            url='https://www.kbb.com/owners-argo/api/',
            data={
                'operationName': 'yearsQuery',
                'variables': {},
                'query': 'query yearsQuery {\n  data: years(vehicleClass: \"UsedCar\") {\n    value: id\n    text: id\n    __typename\n  }\n}',
            },
            callback=self.parse_years,
            cb_kwargs={
                'result': result,
            },
        )

    def parse_years(self, response, result):
        json_response = response.json()

        result['years'] = {}

        year_ids = [item['text'] for item in json_response['data']['data']]

        yield self.iterate_years(year_ids, result)

    def iterate_years(self, year_ids, result):
        if len(year_ids) > 0:
            year_id = year_ids.pop(-1)
            year = int(year_id)

            result['years'][year] = {}
            result['years'][year]['makes'] = {}

            return scrapy.http.JsonRequest(
                url='https://www.kbb.com/owners-argo/api/',
                data={
                    'operationName': 'makesQuery',
                    'variables': {
                        'year': year_id,
                    },
                    'query': 'query makesQuery($year: String) {\n  data: makes(vehicleClass: \"UsedCar\", yearId: $year) {\n    value: id\n    text: name\n    __typename\n  }\n}',
                },
                callback=self.parse_makes,
                cb_kwargs={
                    'year_ids': year_ids,
                    'year': year,
                    'year_id': year_id,
                    'result': result,
                },
            )
        else:
            return result

    def parse_makes(self, response, year_ids, year, year_id, result):
        json_response = response.json()

        makes = [item['text'] for item in json_response['data']['data']]
        make_ids = [item['value'] for item in json_response['data']['data']]

        self.iterate_makes(year_ids, makes, make_ids, year, year_id, result)

    def iterate_makes(self, year_ids, makes, make_ids, year, year_id, result):
        if len(makes) > 0:
            make = makes.pop(-1)
            make_id = make_ids.pop(-1)

            result['years'][year]['makes'][make] = {}
            result['years'][year]['makes'][make]['models'] = {}

            return scrapy.http.JsonRequest(
                url='https://www.kbb.com/owners-argo/api/',
                data={
                    'operationName': 'modelsQuery',
                    'variables': {
                        'year': year_id,
                        'make': make_id,
                    },
                    'query': 'query modelsQuery($year: String, $make: String) {\n  data: models(vehicleClass: \"UsedCar\", yearId: $year, makeId: $make) {\n    value: id\n    text: name\n    __typename\n  }\n}',
                },
                callback=self.parse_models,
                cb_kwargs={
                    'year_ids': year_ids,
                    'makes': makes,
                    'make_ids': make_ids,
                    'year': year,
                    'year_id': year_id,
                    'make': make,
                    'result': result,
                },
            )
        else:
            return self.iterate_years(year_ids, result)

    def parse_models(self, response, year_ids, makes, make_ids, year, year_id, make, result):
        json_response = response.json()

        models = [item['text'] for item in json_response['data']['data']]

        self.iterate_models(year_ids, makes, make_ids,
                            models, year, year_id, make, result)

    def iterate_models(self, year_ids, makes, make_ids, models, year, year_id, make, result):
        if len(models) > 0:
            model = models.pop(-1)

            result['years'][year]['makes'][make]['models'][model] = {}

            return scrapy.http.JsonRequest(
                url='https://www.kbb.com/owners-argo/api/',
                data={
                    'operationName': 'stylesPageQuery',
                    'variables': {
                        'make': self.special_character_except_dash_and_underscore_pattern.sub('', make.lower().replace(' ', '-')),
                        'model': self.special_character_except_dash_and_underscore_pattern.sub('', model.lower().replace(' ', '-')),
                        'year': year_id,
                    },
                    'query': 'query stylesPageQuery($year: String, $make: String, $model: String) {\n  ymm: stylesPage(\n    vehicleClass: \"UsedCar\"\n    year: $year\n    make: $make\n    model: $model\n  ) {\n    year\n    make {\n      id\n      name\n      __typename\n    }\n    model {\n      id\n      name\n      __typename\n    }\n    bodyStyles {\n      name\n      trims {\n        id\n        name\n        vehicleId\n        __typename\n      }\n      defaultVehicleId\n      __typename\n    }\n    typicalMileage\n    defaultVehicleId\n    subCategory\n    searchNewCarYear\n    chromeStyleId\n    __typename\n  }\n}',
                },
                callback=self.parse_trims,
                cb_kwargs={
                    'year_ids': year_ids,
                    'makes': makes,
                    'make_ids': make_ids,
                    'models': models,
                    'year': year,
                    'year_id': year_id,
                    'make': make,
                    'model': model,
                    'result': result,
                },
            )
        else:
            return self.iterate_makes(year_ids, makes, make_ids, year, year_id, result)

    def parse_trims(self, response, year_ids, makes, make_ids, models, year, year_id, make, model, result):
        json_response = response.json()

        trims = [trim['name'] for body_style in json_response['data']
                 ['ymm']['bodyStyles'] for trim in body_style['trims']]

        result['years'][year]['makes'][make]['models'][model]['trims'] = trims

        self.iterate_models(year_ids, makes, make_ids,
                            models, year, year_id, make, result)
