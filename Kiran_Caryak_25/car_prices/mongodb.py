import car_prices.config as config
from pymongo import MongoClient
import atexit


class Database:
    def __init__(self, database_config: config.Database):
        self.client = MongoClient(
            f'mongodb://{database_config.username}:{database_config.password}@{database_config.host}:{database_config.port}/',
            tls=True,
            tlsCAFile=database_config.ca_file,
            retryWrites=False,
        )
        self.database_name = database_config.name
        atexit.register(self.close)

    def close(self):
        self.client.close()

    @property
    def handle(self):
        return self.client[self.database_name]

