import scrapy
import scrapy.http
import re
from car_prices.spiders.car_prices import car_prices_spider
from car_prices.exceptions import ProxyBlocked


class CarPricesAllCarSpider(car_prices_spider(source='AllCars')):
    captcha_site_key = '6LdRnw0eAAAAAEg2RoKjdjl50TA_eGWmz4zwyydX'

    site_conditions = {
        'bad': 'Needs Lots Of Love',
        'moderate': 'Seen Better Days',
        'good': 'Used Modestly',
        'excellent': 'Used Modestly',
    }

    condition_codes = {
        'bad': 'Needs Lots Of Love',
        'moderate': 'Seen Better Days',
        'good': 'Used Modestly',
        'excellent': 'Used Modestly',
    }

    def answers_to_offer_questions(self, condition):
        return {
            'What is the condition of the vehicle?': self.site_conditions[condition],
            'Has the vehicle been in an accident?': 'No Accidents',
            'Optional Equipment': [],
            'Title Present': 'Yes',
            'Title Issues': 'No',
            'Frame Damage': 'No',
            'Glass Damage': 'No',
            'Rust Damage': 'No',
            'Body Damage': 'No',
            'Engine Issues': 'No',
            'Interior Issues': 'No',
            'Mechanical Issues': 'No',
            'Warning Lights': 'No',
            'Modifications': 'No',
            'Tire Issues': 'No',
            'Tire Tread': 'No',
            'Transmission': 'No',
        }

    def process_requests(self, result):
        condition = result['condition']
        result['answers'] = self.answers_to_offer_questions(condition)

        offer_page_response = yield scrapy.Request(
            method='GET',
            url='https://cars.allcars.com/sell-your-car',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                # "DNT": "1",
                # "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
        )

        if offer_page_response.status == 403:
            raise ProxyBlocked

        csrf_token = offer_page_response.xpath(
            '/html/head/meta[@name="csrf-token"]/@content').get()

        personal_info_captcha_result = yield from self.solving_recaptchav2_coroutine(
            website_url='https://cars.allcars.com/sell-your-car',
            website_key=self.captcha_site_key,
            proxy=result['proxy']
        )

        personal_info_captcha_solution_token = personal_info_captcha_result

        personal_info_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url='https://cars.allcars.com/sell-your-car/your_info',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6InZ4SU5YOVhLKzdyajRVampFVjVCL1E9PSIsInZhbHVlIjoiemQ1ME1QTFlMbXdxZExMSVdWL2VZblE0cUhjcEdnZ0RlT0pHK01KcnA1anFGYlZ0TXE0YlhWYnVpclBaVzhrb2lLWndMSjFKUzRmeThoT0V1d1RRdXY1UldidWlpWVBVU3JpZkVCTkl2K3lsMFFUSUErOXhINUwwQkU3c3JhQngiLCJtYWMiOiJhNDUxMDZhNGYzZGQwYTZjYjQ4ZGI2MjhkMWJkYzVjNzBjMDVkZmI0OGY1Yjk3OGI2NWY2ZWRlMWU0ZTk1MjQwIiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6InZ4SU5YOVhLKzdyajRVampFVjVCL1E9PSIsInZhbHVlIjoiemQ1ME1QTFlMbXdxZExMSVdWL2VZblE0cUhjcEdnZ0RlT0pHK01KcnA1anFGYlZ0TXE0YlhWYnVpclBaVzhrb2lLWndMSjFKUzRmeThoT0V1d1RRdXY1UldidWlpWVBVU3JpZkVCTkl2K3lsMFFUSUErOXhINUwwQkU3c3JhQngiLCJtYWMiOiJhNDUxMDZhNGYzZGQwYTZjYjQ4ZGI2MjhkMWJkYzVjNzBjMDVkZmI0OGY1Yjk3OGI2NWY2ZWRlMWU0ZTk1MjQwIiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6Imx6bVVWeVZVS0NBL21MTmNxMWhCU1E9PSIsInZhbHVlIjoia2Zpb01jRDRSZU5sQlErSkxncUhOUWYzdUpnckNUR2ZBLzFUcHdNT0tjNGl4SFdRcThUTUtYQ3FVQW9TZUhHUHJVL2h2VXpSN2ZUclkrbytyOXlZU1RrNjMzeldvUFl2U05xamlBcU5FVmNIeDhYbElUR3lDOUtUQXE1dlpSVkciLCJtYWMiOiJkYzkxNTE2NjhiZDM1Y2E5OTg1ODhmYjJjYmI5ZTQ4MDNlN2ZhOGUyM2E2OGJkNmZhNDg2NmNlY2NhYzJmYTRjIiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
            data={
                "first_name": result['first_name'],
                "last_name": result['last_name'],
                "email": result['email'],
                "phone_number": re.compile(r'(\d{3})(\d{3})(\d{4})').sub(r'(\1) \2-\3', result['phone_number']),
                "zip_code": result['zip_code'],
                "is_new": True,
                "g-recaptcha-response": personal_info_captcha_solution_token,
            },
        )

        offer_id = personal_info_response.json()['id']

        vin_decoded_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://cars.allcars.com/sell-your-car/vehicle_lookup/{offer_id}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6IjRxeVhyZDEvbjQ3SXp1UEY5NG0rMGc9PSIsInZhbHVlIjoiT1IwTmRBU2llZE9xc2lGdjJyTy90WFZWb3VDUHFDalFEZzVMODAwVWNDaE1hc0JsbGZ1QklxTkY3Z2E3aWJKN0RtdEhnU3lDZk05NzJua1ZFY21Vd2ZxUW1OOEJ4T3ZpTzZOaUtsNEhzWUxFQ2pUV2txaEppYVplbUJBNE5vek4iLCJtYWMiOiJjYTI1ODNmMGEyMDU3ZTIwYjEzMzg2NzljZTUwMzljYmE5MjdmMjMxMzM4NTFkMTA1ZGU5MDg2MGM0MWE0OGI0IiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6IjRxeVhyZDEvbjQ3SXp1UEY5NG0rMGc9PSIsInZhbHVlIjoiT1IwTmRBU2llZE9xc2lGdjJyTy90WFZWb3VDUHFDalFEZzVMODAwVWNDaE1hc0JsbGZ1QklxTkY3Z2E3aWJKN0RtdEhnU3lDZk05NzJua1ZFY21Vd2ZxUW1OOEJ4T3ZpTzZOaUtsNEhzWUxFQ2pUV2txaEppYVplbUJBNE5vek4iLCJtYWMiOiJjYTI1ODNmMGEyMDU3ZTIwYjEzMzg2NzljZTUwMzljYmE5MjdmMjMxMzM4NTFkMTA1ZGU5MDg2MGM0MWE0OGI0IiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6IjZvNWcxQVNyUkpLcVUxdjczM1hRN1E9PSIsInZhbHVlIjoiWmQ2ODY5SFp2aE1nN0VjWmdEV0lmeW1hN0JiZVpLaDBqMnFza09KekdxcjhBRWE2eHZDRmVYd1BMSXV2SGU1Mkw2YjRLeGMvUkpZbTU5ZksyUjlNcFAzZHp4MnlzVWhVU01uV1dZMjlycEtVR1FXNlU1Vk9zVTJSNzduUlZReGsiLCJtYWMiOiIxOTA4YTVlOGMwZDViMTk4NGQxZmNmYmZhNjEzZGY1NmFjNjc3ZWU2MWQzNmUyOTE5NDgwMGFlYWFkMWM2Mzk2IiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
            data={
                "vin": result['vin_number'],
                "is_new": True,
                "plate": None,
                "plateState": None,
                "year": None,
                "make": None,
                "model": None,
                "trim": None,
                "uvc": None,
                "style_list": None,
                "type": "sCVin"
            },
        )

        vin_data = vin_decoded_response.json()['vin_data']
        mileage = f'{result["mileage"]:,}'
        style = None  # '4D SUV AWD'
        style_code = None  # '2017640313'
        color = 'Black'

        vehicle_details_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://cars.allcars.com/sell-your-car/drivably/additional_info/{offer_id}',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6IjNQZnh0NHpwYmI3Y0MzRUZQZTl4emc9PSIsInZhbHVlIjoiYk1qblJ4cDJySWF3NXFQdmhUUW8vZUprWDNEeEhLSEd3Nk5xNXllMktmeG5oeVlFUHRXR3FiTWNFS0hrdmhXeGx6Y2Jzc3djYTJMS01NL1U3ZmExV0xnS1JNN2F3WnRlYThuWUNSWXJnVUN0Q3BtVHp2ZTY4K1E1cHlvdkVNcVQiLCJtYWMiOiJhZDU1ZGQ2NjUyM2RkNjRiMGUzZGU5ZTE4MDhjMzRmMDY2ZjUwNDdiYzE2N2E1YWNlMGZkZDY5OWY0NmZlMzE3IiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6IjNQZnh0NHpwYmI3Y0MzRUZQZTl4emc9PSIsInZhbHVlIjoiYk1qblJ4cDJySWF3NXFQdmhUUW8vZUprWDNEeEhLSEd3Nk5xNXllMktmeG5oeVlFUHRXR3FiTWNFS0hrdmhXeGx6Y2Jzc3djYTJMS01NL1U3ZmExV0xnS1JNN2F3WnRlYThuWUNSWXJnVUN0Q3BtVHp2ZTY4K1E1cHlvdkVNcVQiLCJtYWMiOiJhZDU1ZGQ2NjUyM2RkNjRiMGUzZGU5ZTE4MDhjMzRmMDY2ZjUwNDdiYzE2N2E1YWNlMGZkZDY5OWY0NmZlMzE3IiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6InYrZENOekx5R09hWTdhb05MVUJTM1E9PSIsInZhbHVlIjoiNytNdkVyUWxIaXN4QlhQT0YxYlcyZ2gxZHQvODFpcmhyYnhnNUdGM3docjhMYTREZHRqVThPMXI3R1ZYM1UrOC9IZ3VPNUJOMWE1K2F0K3FEREtsN0RxOU9kTjVwYS94UlZKTi9vZDE1MFluYm9vM3pFL0ZUcU5sd21HMDl5TmIiLCJtYWMiOiJhYzI5YTg1YTZjYWZmNmZiNTljYzU2MTU4NDU1YTdhZjZjNjkwYTNkZTE3YzM2NGJmZGNlMDZkYjY2YmJkNzBmIiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
            data={
                "year": None,
                "make": None,
                "model": None,
                "trim": None,
                "style": style,
                "color": color,
                "mileage": mileage,
                "zip_code": result['zip_code'],
                "uvc": style_code,
                "isMakeModelNotShown": False
            },
        )

        transmission = 'Auto' if 'auto' in result['transmission'].lower(
        ) else 'Manual'

        vehicle_transmission_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://cars.allcars.com/sell-your-car/drivably/additional_info/{offer_id}/condition/inputs_transmission',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6IngyMXdxenozN0VoK3BPd2ltUisxY1E9PSIsInZhbHVlIjoiZGdWczZmODJNMmlZOUhVeWtrWHFRQXlkTTVQME1HVzN2bXVKaUt5U3E3K2QzVFY5M09oM1Vqc2NzZ0ZDREVMTXFiaEh4a3RuMlhWRk9UcTN5a1hXeVZ4T0lIS1FXSGhSNXp4SXBvQzFWVFhham9uQjNtMGtqTGZ6YjI4SmdJQkMiLCJtYWMiOiI3MDA4ZGI1NDJlY2U4YjkxODRlYzI4YWY5ZDY0NmZkNThmMDZlMWQ3MzI2ZTE0MjY5YjkwNjEzZWQ5N2FhMzhiIiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6IngyMXdxenozN0VoK3BPd2ltUisxY1E9PSIsInZhbHVlIjoiZGdWczZmODJNMmlZOUhVeWtrWHFRQXlkTTVQME1HVzN2bXVKaUt5U3E3K2QzVFY5M09oM1Vqc2NzZ0ZDREVMTXFiaEh4a3RuMlhWRk9UcTN5a1hXeVZ4T0lIS1FXSGhSNXp4SXBvQzFWVFhham9uQjNtMGtqTGZ6YjI4SmdJQkMiLCJtYWMiOiI3MDA4ZGI1NDJlY2U4YjkxODRlYzI4YWY5ZDY0NmZkNThmMDZlMWQ3MzI2ZTE0MjY5YjkwNjEzZWQ5N2FhMzhiIiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6ImpEYkw3U3lULzNhRHBwZS9xUlYzK0E9PSIsInZhbHVlIjoiTWhBZllQbVdWRHJwYmdZUlE1eXBGeXhqZm51STRvSXpwNzEzTVovNDJnWDNjcnd6UjAvcW0rOGZWUFVVbjVURFFrM0RsN3RNMXFyUUJReWZCVHhsZ1dody9vUkNKRlJOczJybXp4NTZZcnBuYWh3N1FKNmZhcE1Vb1owWDN3V2siLCJtYWMiOiIwOTE0YjM0ZGNkOGU3NDdhNDY4Mzk0YjYxZWRkNGZhOWY5MDk3MDk1MzI3NTk1NGY4YzA3NDNhZGViYTAyN2NlIiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            },
            data={
                "value": transmission
            },
        )

        terms_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://cars.allcars.com/sell-your-car/drivably/additional_info/{offer_id}/condition/agreeOnTerms',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6IjdsZS94aFdoMWhvekMrUkUwclZISXc9PSIsInZhbHVlIjoiSWlyY09yemJSNHY4bUhLbmp3L09XbHpMTjkzTXlPYTZZMXd4TGhJZWJPUTVicDZpZkNKcFZjUWswOUJYRVMxNWpnTHVwQUxPSXpWREE0VEFQbVFpb2pJM28wRHNtaEFxcmVoc0JJOFYxYVpEcVZkUmNCcGJ5SWdFVG5QUzVOangiLCJtYWMiOiJjMzA2YjA3MDI4NmM2ZTEyZWQxZjE0NzRkNDA5MWViYzBhZTNlZTYwNTY3MWY1ODM5MmMxNzE0NWE4NGJhZGI3IiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6IjdsZS94aFdoMWhvekMrUkUwclZISXc9PSIsInZhbHVlIjoiSWlyY09yemJSNHY4bUhLbmp3L09XbHpMTjkzTXlPYTZZMXd4TGhJZWJPUTVicDZpZkNKcFZjUWswOUJYRVMxNWpnTHVwQUxPSXpWREE0VEFQbVFpb2pJM28wRHNtaEFxcmVoc0JJOFYxYVpEcVZkUmNCcGJ5SWdFVG5QUzVOangiLCJtYWMiOiJjMzA2YjA3MDI4NmM2ZTEyZWQxZjE0NzRkNDA5MWViYzBhZTNlZTYwNTY3MWY1ODM5MmMxNzE0NWE4NGJhZGI3IiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6IkhHOUh0SXNnQUVOT25CdWc4cHZHOHc9PSIsInZhbHVlIjoibXhmRHo3dWlUWDk3dmNqbGdWeUhIblVBeUtPTlk3eGhpZ1VqV0ZQVWVNTUk1eFVTbnYxSGR3ZmlhSlhUbi9LVkhlV0lEWmJpRlhaZUhpNVFQRnlpakRKNUhQeEl2VTRvUlEvRUFWYit5NEM1K1g2Z3BuNDBnN2dCR3dadzAxL3kiLCJtYWMiOiI3MDJmNThlOTk2YTlkNjE0ZDA5NzBhYTExNWIwNWZiMDI5MWRhZWExMjc0ZjY5ZGUxYTA0M2ZkNzQ0YTA0OTRhIiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "value": True
            },
        )

        site_condition = self.site_conditions[condition]

        condition_data = {
            "vehicle_condition": site_condition,
            "vehicle_accident": "No Accidents",
            "optional_equipment": None,
            "title_present": "Yes",
            "title_issues": "No",
            "frame_damage": "No",
            "glass_damage": "No",
            "rust_damage": "No",
            "rust_damage_true": [],
            "body_damage": "No",
            "body_damage_true": [],
            "engine_issues": "No",
            "engine_issues_true": [],
            "interior_issues": "No",
            "interior_issues_true": [],
            "mechanical_issues": "No",
            "mechanical_issues_true": [],
            "warning_lights": "No",
            "warning_lights_true": [],
            "modifications": "No",
            "modifications_true": [],
            "tire_issues": "No",
            "tire_issues_true": [],
            "tire_tread": "Good",
            "transmission": transmission,
        }

        vehicle_conditions_response = yield scrapy.http.JsonRequest(
            method='PATCH',
            url=f'https://cars.allcars.com/sell-your-car/drivably/additional_info/{offer_id}/condition',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6Inl0V1FSUEJuMHRBVkJ2RTd5RHJvYUE9PSIsInZhbHVlIjoidGV0SklRYmp0VERvaDNyK0poU0NuSW1XeEE0TDlPenE3QTNqNWtabjVWVzFwY3dnZWt0MVJrUXh1MWwyQ2p5NXZycTdqTmM5ZktmbTd3U3lyVVhqRU8wdEYvclpxa0NVVU9sc3JuU052OEpyM2IrNElESGExYnI1V3R1S05ncWwiLCJtYWMiOiI2NGRkY2FlMWQ2Y2ExZGNlOTNlZjhlZWU4MzFhY2Y4YTVmYmRjMzRmMmQ4MWQ3Yzk3NDYzNmVlMGRiZjRkMGJkIiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6Inl0V1FSUEJuMHRBVkJ2RTd5RHJvYUE9PSIsInZhbHVlIjoidGV0SklRYmp0VERvaDNyK0poU0NuSW1XeEE0TDlPenE3QTNqNWtabjVWVzFwY3dnZWt0MVJrUXh1MWwyQ2p5NXZycTdqTmM5ZktmbTd3U3lyVVhqRU8wdEYvclpxa0NVVU9sc3JuU052OEpyM2IrNElESGExYnI1V3R1S05ncWwiLCJtYWMiOiI2NGRkY2FlMWQ2Y2ExZGNlOTNlZjhlZWU4MzFhY2Y4YTVmYmRjMzRmMmQ4MWQ3Yzk3NDYzNmVlMGRiZjRkMGJkIiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6IndDVXk0cFlQejZoeW56eXJlbldrdHc9PSIsInZhbHVlIjoiM0FTWjNvS3NzdTZqazNacndrUHZMQ3pjVy9HVHNSbWFVNWZBU2tDNzN2dXFXaUV3WG1DSW9aamVTZEc0Nnl3RTlqWWF3bTJzdTBxdHNZZERydGc0bXNMVTRweENZSXkvdG40QUhQcDdtVUI3TTRkNmkxL1c5ZXI1MENIRDJlcTQiLCJtYWMiOiJiOTg0YzY0ZTAwYWY3MTQ3YjhjOTg4ODExMDNiOTVhMTJjODhiMjY4MTZjMzQ2ZDgzNzBlNTdiMjE1NjY4Yzc0IiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data=condition_data | {
                "agreeOnTerms": True,
                "textMessageTerms": False
            },
        )

        vin_data['attributes'] = {
            "style": style,
            "color": color,
            "mileage": mileage,
            "zip_code": result['zip_code'],
            "conditions": condition_data,
        } | vin_data['attributes']

        offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url=f'https://cars.allcars.com/sell-your-car/drivably/additional_info/{offer_id}/execute-node-offer-scraper',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://cars.allcars.com/sell-your-car",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-TOKEN": csrf_token,
                "Content-Type": "application/json;charset=utf-8",
                # "X-XSRF-TOKEN": "eyJpdiI6IlFCV3k5UHZPN1Y2Vm9nUTkyZnFtbVE9PSIsInZhbHVlIjoiY3duWEFSME1Bc2s4Wm5NZXlmekxBVk5oM0xDbjJrZ1pMYWJrZkUwTE4yYTBaSHBuUE01ZGFQZkZDSUhBMEpSaUFHVmU2VWYvSDNIVHRzbUlDdkNRTW44S2VDV1pTU3drNGtidXFhNWpYMlZSZWJDNHVzdE1oZWlhcURnU3hHY2IiLCJtYWMiOiI2Y2QzZWFkYzVmYTkwYzkwZWJmMmY5ZjFlNWM0NWM0Y2Y4ZDliOGY5MTcyNzkxZWU4M2UzNDg0NjQ3NjAyY2M2IiwidGFnIjoiIn0=",
                "Origin": "https://cars.allcars.com",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "XSRF-TOKEN=eyJpdiI6IlFCV3k5UHZPN1Y2Vm9nUTkyZnFtbVE9PSIsInZhbHVlIjoiY3duWEFSME1Bc2s4Wm5NZXlmekxBVk5oM0xDbjJrZ1pMYWJrZkUwTE4yYTBaSHBuUE01ZGFQZkZDSUhBMEpSaUFHVmU2VWYvSDNIVHRzbUlDdkNRTW44S2VDV1pTU3drNGtidXFhNWpYMlZSZWJDNHVzdE1oZWlhcURnU3hHY2IiLCJtYWMiOiI2Y2QzZWFkYzVmYTkwYzkwZWJmMmY5ZjFlNWM0NWM0Y2Y4ZDliOGY5MTcyNzkxZWU4M2UzNDg0NjQ3NjAyY2M2IiwidGFnIjoiIn0%3D; allcars_session=eyJpdiI6InRqMHZvVzg3bE9vRXU2bmNMbUVVUVE9PSIsInZhbHVlIjoiaDFVWGxiYzRkUHUrYjBXR1ArN1dqVVRtNzlQNU5aRGpZeFJ4ZytnekUyWDlFdEtqamZvRmxuZVRpT1J1c2t2Q3hpY1ZtNWlOMTRGQUNyOWRvbnQzUUg0Yy80Tmo0ZlZiMVhzK0lpUlZZRUU1a25CaFZsekp2Q1ZQT1hkd2Mzc3MiLCJtYWMiOiJiNTg0YTk4MDhkY2Y4ZjY2NWQxZmM2YmJlMWIxZjNjMTQyODRmZmZkYTFlYjI1NTg5ODZkMzEyYzkxNjVjZjkwIiwidGFnIjoiIn0%3D; _gcl_au=1.1.843176197.1679461517; _uetsid=24ca54e0c86f11edb0d8270dfbe3149a; _uetvid=24ca5050c86f11edb59c038183600824; prism_610304056=881e92e8-c783-4b6b-9166-858e4ca9b0ca",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            data={
                "vin": result['vin_number'],
                "is_new": True,
                "plate": None,
                "plateState": None,
                "year": None,
                "make": None,
                "model": None,
                "trim": None,
                "uvc": style_code,
                "style_list": None,
                "type": "sCVin",
                "vin_data": vin_data,
            },
        )

        offer_data = offer_response.json()['offer_data']
        if 'drivably' in offer_data:
            result['price'] = float(offer_data['drivably'][0])
        else:
            result['success'] = 'At this time, due to the value of your vehicle, we will have to finalize your offer.'

        yield result
