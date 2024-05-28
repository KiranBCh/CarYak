import os
from datetime import datetime
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name         = 'caryak',
        version      = '1.0',
        packages     = find_packages(),
        entry_points = {'scrapy': ['settings = car_prices.settings']},
    )

    filename = os.listdir('dist')[0]
    os.rename(f'dist/{filename}', f'eggs/caryak/{int(datetime.utcnow().timestamp())}.egg')

