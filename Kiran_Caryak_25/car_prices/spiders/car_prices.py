from car_prices.spiders.basic import Result, basic_spider


def car_prices_spider(source: str):
    class Spider(basic_spider(source=source, category='car_prices')):
        def __init__(
            self,
            batch_com: str,
            batch_id: str,
            vin: str,
            trim: str,
            condition: str,
            mileage: str,
            zip_code: str,
            *args,
            **kwargs
        ):
            super().__init__(batch_com=batch_com, batch_id=batch_id, *args, **kwargs)

            self.vin = vin.upper()
            self.trim = trim.lower()
            self.condition = condition.lower()
            self.mileage = int(mileage)
            self.zip_code = zip_code

        def get_additional_result_details(self) -> Result:
            return {
                'batch_id': self.batch_id,
                'batch_com': self.batch_com,
                'vin_number': self.vin,
                'trim': self.trim,
                'condition': self.condition,
                'mileage': self.mileage,
                'zip_code': self.zip_code,
            }

    return Spider
