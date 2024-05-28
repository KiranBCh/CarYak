import scrapy
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesAutoNationSpider(car_prices_spider(source='AutoNation')):
    def answers_to_offer_questions(self):
        return {
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions()

        result['success'] = False
        yield result
