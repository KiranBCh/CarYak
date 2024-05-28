import scrapy
from datetime import datetime


class CargurusSpider(scrapy.Spider):
    name = 'cargurus'
    collection_name = 'vins'

    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    cars_per_page = 15

    def page_request(self, page_number):
        'https://www.cargurus.com/Cars/getCarPickerReferenceDataAJAX.action?showInactive=false&useInventoryService=true&localCountryCarsOnly=true&outputFormat=REACT&quotableCarsOnly=false'
        make_model = '&entitySelectingHelper.selectedEntity=d2137' if hasattr(
            self, 'make') else ''
        min_year = '&startYear=2015' if hasattr(self, 'min_year') else ''
        max_year = '&endYear=2020' if hasattr(self, 'max_year') else ''
        body_type = '&bodyTypeGroupIds=0' if hasattr(self, 'body_type') else ''
        features = '&installedOptionIds=140&installedOptionIds=6' if hasattr(
            self, 'features') else ''
        max_mileage = '&maxMileage=9999999' if hasattr(
            self, 'max_mileage') else ''
        min_price = '&minPrice=0' if hasattr(self, 'min_price') else ''
        max_price = '&maxPrice=9999999' if hasattr(self, 'max_price') else ''

        return scrapy.Request(
            # url=f'https://www.cargurus.com/Cars/searchResults.action?zip=77381&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&showNegotiable=false&shopByTypes=NEAR_BY&sortDir=DESC&sourceContext=untrackedWithinSite_false_0&distance=50000&sortType=AGE_IN_DAYS&offset={index*cars_per_page}&maxResults={cars_per_page}&filtersModified=true{make_model}{min_year}{max_year}{body_type}{features}{max_mileage}{min_price}{max_price}',
            url=f'https://www.cargurus.com/Cars/searchResults.action?zip=77381&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&nonShippableBaseline=0&shopByTypes=NEAR_BY&sortDir=ASC&sourceContext=untrackedWithinSite_false_0&distance=50000&sortType=DEAL_RATING_RPL&offset={page_number*self.cars_per_page}&maxResults={self.cars_per_page}&filtersModified=true',
            callback=self.parse_cargurus_search_page,
            cb_kwargs={'page_number': page_number},
        )

    def start_requests(self):
        yield self.page_request(0)

    def parse_cargurus_search_page(self, response, page_number):
        json_response = response.json()

        for car in json_response:
            result = {
                'datetime': datetime.utcnow(),
                'source': 'CarGurus',
                'vin_number': car['vin']
            }

            if 'listingTitle' in car:
                result['name'] = car['listingTitle']

            if 'makeName' in car:
                result['make'] = car['makeName']

            if 'modelName' in car:
                result['model'] = car['modelName']

            if 'carYear' in car:
                result['year'] = car['carYear']

            if 'bodyTypeName' in car:
                result['body_type'] = car['bodyTypeName']

            if 'options' in car:
                result['features'] = car['options']

            if 'mileage' in car:
                result['mileage'] = car['mileage']

            if 'price' in car:
                result['price'] = car['price']

            yield result

        if len(json_response) >= self.cars_per_page:
            yield self.page_request(page_number+1)
