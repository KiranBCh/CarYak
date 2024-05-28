from dataclasses import dataclass
from random import randrange
import scrapy
import scrapy.http
from datetime import datetime, timezone
from car_prices.exceptions import CantMakeOfferForVin, OfferAlreadyExists, ProxyBlocked, UnknownDealer, VinNotFound
from car_prices.spiders.car_prices import car_prices_spider
import time


@dataclass
class Account:
    first_name: str
    last_name: str
    email: str
    phone_number: str
    zip_code: str
    street_address: str
    password: str


accounts = [
    Account(
        first_name='Ashleigh',
        last_name='Doyle',
        email='k.ap.u.ro.kiv.i.nce@gmail.com',
        phone_number='(505) 644-2068',
        zip_code='90404',
        street_address='998 Woodland Ave. Freeport, NY',
        password='blimps1!',
    ),
]


class CarPricesTrueCarSpider(car_prices_spider(source='TrueCar')):
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    colour_map = {
        "Black": "Black",
        "White": "White",
        "Pearl White": "White",
        "Grey": "Gray",
        "Light Blue": "Blue",
        "Dark Blue": "Blue",
        "Dark Green": "Green",
        "Charcoal Grey": "Gray",
        "Silver": "Silver",
        "Light Green": "Green",
        "Tan": "Tan",
        "Brown": "Brown",
        "Beige": "Beige",
        "Red": "Red",
        "Purple": "Purple",
        "Burgundy": "Maroon",
        "Yellow": "Yellow",
        "Orange": "Orange",
        "Gold": "Gold",
        "Bright Blue": "Blue",
        "Bright Green": "Green"
    }

    def answers_to_offer_questions(self):
        return {
            'What type of title does the vehicle have?': 'Clean',  # Clean, Salvage, Rebuilt
            'Is the vehicle owned outright?': 'Yes',  # Yes, No
            'Is the title in the sellers possession?': 'Yes',  # Yes, No
            'Has the vehicle ever been in an accident?': 'No',  # No, Yes
            'Are there any minor defects or damage to the body panels?': 'No',  # No, Yes
            'Is there significant damage to the body panels?': 'No',  # No, Yes
            'Does the windshield require replacement?': 'No',  # No, Yes
            'Any damage to the other windows, mirrors, or lights?': 'No',  # No, Yes
            # Hail Damage, Undercarriage Damage, Flood Damage, Fire Damage, None of the above
            'Has any of the following happened to the vehicle?': 'None of the above',
            'What is the seat material?': 'Cloth',  # Cloth, Leater
            'Has the vehicle been smoked in?': 'No',  # No, Yes
            'Do the seats have any burns, stains, rips or tears?': 'No',  # No, Yes
            'Is anything damaged or inoperable?': 'No',  # No, Yes
            'Are there any mechanical issues with the vehicle?': 'No',  # No, Yes
            'Are there any fluid leaks?': 'No',  # No, Yes
            'Are there any aftermarket parts installed?': 'No',  # No, Yes
            'How many keys do you have?': '2+',  # 0, 1, 2+
            # Never, 0-1 year ago, 1-2 years ago, 2-3 years ago, 3+ years ago
            'Approximately when were all the tires last replaced?': 'Never',
            'Are there any issues with the tires?': 'No',  # No, Yes
            'Are there any issues with the wheels?': 'No',  # No, Yes
        }

    def process_requests(self, result):
        result['answers'] = self.answers_to_offer_questions()

        random_account = accounts[randrange(len(accounts))]

        # Getting the necessary cookies.
        yield scrapy.Request(
            method='GET',
            url='https://www.truecar.com/sell-your-car/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            },
        )

        # Logging zip code validation
        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.truecar.com/abp/api/graphql/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.truecar.com/sell-your-car/",
                "content-type": "application/json",
                "apollographql-client-name": "abp-frontend",
                "authorization-mode": "consumer",
                # "Content-Length": "251",
                "Origin": "https://www.truecar.com",
                "Connection": "keep-alive",
                # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:2$_ss:0$_st:1695953845277$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:1%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695952955416; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952048.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952048.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            },
            data={
                "operationName": "VinForm_zipCodeGeolocation",
                "variables": {
                    "postalCode": result['zip_code']
                },
                "query": "query VinForm_zipCodeGeolocation($postalCode: String!) {\n  geolocation(postalCode: $postalCode) {\n    id\n    postalCode\n    state\n    __typename\n  }\n}\n"
            },
        )

        vin_decoded_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.truecar.com/abp/api/graphql/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.truecar.com/sell-your-car/",
                "content-type": "application/json",
                "apollographql-client-name": "abp-frontend",
                "authorization-mode": "consumer",
                # "Content-Length": "706",
                "Origin": "https://www.truecar.com",
                "Connection": "keep-alive",
                # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:2$_ss:0$_st:1695953845277$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:1%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695952955416; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952048.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952048.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            },
            data={
                "operationName": "SYCVehicleForm_DecodeVin",
                "variables": {
                    "vin": result['vin_number']
                },
                "query": "query SYCVehicleForm_DecodeVin($vin: String!) {\n  decodeVin(vin: $vin) {\n    id\n    name\n    databaseId\n    trim {\n      id\n      slug\n      __typename\n    }\n    model {\n      id\n      name\n      slug\n      year\n      make {\n        id\n        slug\n        name\n        __typename\n      }\n      styles(active: RETAIL) {\n        nodes {\n          id\n          name\n          databaseId\n          trim {\n            id\n            slug\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            },
        )

        decoded_vins = vin_decoded_response.json()['data']['decodeVin']

        if not decoded_vins:
            raise VinNotFound

        possible_vehicles = [(
            int(possibility['databaseId']),
            possibility['model']['make']['slug'],
            possibility['model']['slug'],
            possibility['trim']['slug'],
            possibility['name'],
        ) for possibility in decoded_vins if possibility['model']['year'] == result['year']]

        vehicle_scores = []

        yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.truecar.com/abp/api/graphql/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.truecar.com/trade/appraisal/{result['vin_number']}/?source=syc",
                "content-type": "application/json",
                "apollographql-client-name": "abp-frontend",
                "authorization-mode": "consumer",
                # "Content-Length": "1420",
                "Origin": "https://www.truecar.com",
                "Connection": "keep-alive",
                # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:5$_ss:0$_st:1695953857689$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:4%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695952957886; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952057.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952057.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            },
            data={
                "operationName": "TcoAppraisal_Questionnaire",
                "variables": {},
                "query": "query TcoAppraisal_Questionnaire {\n  questionnaire {\n    questions {\n      key\n      label\n      order\n      section\n      type\n      helperText\n      options {\n        label\n        order\n        value\n        helperText\n        exclusive\n        subQuestions {\n          key\n          label\n          order\n          section\n          type\n          helperText\n          validations {\n            type\n            value\n            __typename\n          }\n          options {\n            label\n            order\n            value\n            helperText\n            exclusive\n            subQuestions {\n              key\n              label\n              order\n              section\n              type\n              helperText\n              validations {\n                type\n                value\n                __typename\n              }\n              options {\n                label\n                order\n                value\n                helperText\n                exclusive\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      validations {\n        type\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            },
        )

        for style_id, make, model, trim, name in possible_vehicles:
            colours_response = yield scrapy.http.JsonRequest(
                method='POST',
                url='https://www.truecar.com/abp/api/graphql/',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": f"https://www.truecar.com/trade/appraisal/{result['vin_number']}/?source=syc",
                    "content-type": "application/json",
                    "apollographql-client-name": "abp-frontend",
                    "authorization-mode": "consumer",
                    # "Content-Length": "797",
                    "Origin": "https://www.truecar.com",
                    "Connection": "keep-alive",
                    # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:14$_ss:0$_st:1695953868709$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:13%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695952970169; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952060.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952060.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "TE": "trailers"
                },
                data={
                    "operationName": "SYCStyleContext_GetColors",
                    "variables": {
                        "styleId": style_id
                    },
                    "query": "query SYCStyleContext_GetColors($styleId: Int!) {\n  style(styleId: $styleId) {\n    id\n    colors {\n      nodes {\n        id\n        databaseId\n        genericName\n        name\n        rgbHex\n        twoToneRgbHex\n        category\n        __typename\n      }\n      __typename\n    }\n    options {\n      nodes {\n        id\n        category\n        features\n        colors {\n          nodes {\n            id\n            databaseId\n            genericName\n            name\n            rgbHex\n            twoToneRgbHex\n            category\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
            )

            colours = [(colour['genericName'], colour['category'], colour['name'])
                       for colour in colours_response.json()['data']['style']['colors']['nodes']]
            exterior_colours = {name: code for name, category,
                                code in colours if category == 'EXTERIOR'}
            interior_colours = {name: code for name, category,
                                code in colours if category == 'INTERIOR'}

            exterior_colour = exterior_colours.get(
                'Black', list(exterior_colours.values())[0]) if exterior_colours else ''
            interior_colour = interior_colours.get(
                'Black', list(interior_colours.values())[0]) if interior_colours else ''

            style_response = yield scrapy.http.JsonRequest(
                method='POST',
                url='https://www.truecar.com/abp/api/graphql/',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": f"https://www.truecar.com/trade/appraisal/{result['vin_number']}/?source=syc",
                    "content-type": "application/json",
                    "apollographql-client-name": "abp-frontend",
                    "authorization-mode": "consumer",
                    # "Content-Length": "693",
                    "Origin": "https://www.truecar.com",
                    "Connection": "keep-alive",
                    # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:16$_ss:0$_st:1695953872133$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:15%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695952972103; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952071.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952071.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "TE": "trailers"
                },
                data={
                    "operationName": "SYCStyleContext_GetStyle",
                    "variables": {
                        "styleId": style_id,
                        "color": exterior_colour
                    },
                    "query": "query SYCStyleContext_GetStyle($styleId: Int!, $color: String!) {\n  style(styleId: $styleId) {\n    id\n    databaseId\n    name\n    engine\n    sideImage: image(cameraAngle: DRIVER_SIDE_PROFILE, colorName: $color, whitestFallback: true) {\n      url\n      __typename\n    }\n    quarterImage: image(cameraAngle: DRIVER_SIDE_FRONT_QUARTER, colorName: $color, whitestFallback: true) {\n      url\n      __typename\n    }\n    model {\n      id\n      name\n      make {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    trimLevel\n    __typename\n  }\n}\n"
                },
            )

            style = style_response.json()['data']['style']
            engine = style['engine']
            image_url = style['sideImage']['url']

            vehicle_scores.append((self.vehicle_aspect_match_score(' '.join(
                [make, model, trim, name, engine]), result['kbb_details']['vehicle_name']), style_id, image_url, exterior_colour, interior_colour))

        vehicle_scores.sort(reverse=True, key=lambda vehicle: vehicle[0])
        vehicle_style_id = vehicle_scores[0][1]
        vehicle_style_image_url = vehicle_scores[0][2]
        vehicle_exterior_colour = vehicle_scores[0][3]
        vehicle_interior_colour = vehicle_scores[0][4]

        start_offer_response = yield scrapy.http.JsonRequest(
            method='POST',
            url='https://www.truecar.com/abp/api/graphql/',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.truecar.com/trade/appraisal/{result['vin_number']}/?source=syc",
                "content-type": "application/json",
                "apollographql-client-name": "abp-frontend",
                "authorization-mode": "consumer",
                # "Content-Length": "1166",
                "Origin": "https://www.truecar.com",
                "Connection": "keep-alive",
                # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:66$_ss:0$_st:1695953932433$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:64%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695953032338; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952121.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952121.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            },
            data={
                "operationName": "generateTrueCashOffer",
                "variables": {
                    "input": {
                        "vin": result['vin_number'],
                        "postalCode": result['zip_code'],
                        "mileage": result['mileage'],
                        "viprStyleId": str(vehicle_style_id),
                        "licensePlateNumber": "",
                        "licensePlateState": "",
                        "interiorColor": vehicle_interior_colour,
                        "exteriorColor": vehicle_exterior_colour,
                        "imageUrl": vehicle_style_image_url,
                        "optionIds": [],
                        "conditions": {
                            "titleType": "clean",
                            "vehicleOwned": True,
                            "titlePossession": True,
                            "hasAccident": False,
                            "bodyPanelMinorDefects": False,
                            "bodyPanelDamage": False,
                            "windshield": False,
                            "windowDamage": False,
                            "damageHistory": [
                                "None of the above"
                            ],
                            "seatMaterial": "cloth",
                            "smoke": False,
                            "seatDamage": False,
                            "interiorDamage": False,
                            "hasMechanicalIssues": False,
                            "fluidLeaks": False,
                            "hasAftermarketAddons": False,
                            "keyCount": "2+",
                            "tireAge": "Never",
                            "hasTireIssues": False,
                            "hasWheelIssues": False
                        },
                        "consumerIntent": "SELL",
                        "source": "SELL_YOUR_CAR"
                    }
                },
                "query": "mutation generateTrueCashOffer($input: GenerateTrueCashOfferInput!) {\n  generateTrueCashOffer(input: $input) {\n    offer {\n      databaseId\n      id\n      offerValueAvailableAt\n      __typename\n    }\n    __typename\n  }\n}\n"
            },
        )

        offer_id = start_offer_response.json(
        )['data']['generateTrueCashOffer']['offer']['databaseId']

        while True:
            yield scrapy.http.JsonRequest(
                method='POST',
                url='https://www.truecar.com/abp/api/graphql/',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                    "content-type": "application/json",
                    "apollographql-client-name": "abp-frontend",
                    "authorization-mode": "consumer",
                    # "Content-Length": "320",
                    "Origin": "https://www.truecar.com",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNzIsImV4cCI6MTcxMTk3MjM3MiwianRpIjoiM2VkZTE0MmQtYjU5Ny00ZDYwLTgzY2EtNDNiZTViYWQ5NmRmIiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiOTA0MDQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=iD3nEv47Doa3-o6wpyDT7NXp5P53pDfqc9Ucfh-bZCY; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:77$_ss:0$_st:1695974180905$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:75%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973280817; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=TUtPRm0rUDJMSjlFSldJSVBiRWFNUEVJaDFtVm4vWFdySmtjd1JCQmRBZTcxZ091cnBXQjdMbjZ6L3Zwb29jYW4zK1JQeGNBaFhXeE5YbHltZXN3TkE9PS0tWnFkNTk1RzMyK1EwOEJQcjJQYVIwdz09--fefb31e7a744d7ebefe79ee7bcfcefcb11e344c4; capselaPreferredPostalCode=90404",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "TE": "trailers"
                },
                data={
                    "operationName": "TcoDashboardPage",
                    "variables": {
                        "offerIdentifier": offer_id
                    },
                    "query": "query TcoDashboardPage($offerIdentifier: ID!) {\n  tcoOffer(offerIdentifier: $offerIdentifier) {\n    id\n    dealerships {\n      id\n      databaseId\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
            )

            offer_availability_response = yield scrapy.http.JsonRequest(
                method='POST',
                url='https://www.truecar.com/abp/api/graphql/',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                    "content-type": "application/json",
                    "apollographql-client-name": "abp-frontend",
                    "authorization-mode": "consumer",
                    # "Content-Length": "604",
                    "Origin": "https://www.truecar.com",
                    "Connection": "keep-alive",
                    # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:68$_ss:0$_st:1695953934440$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:66%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695953033342; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952136.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952136.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "TE": "trailers"
                },
                data={
                    "operationName": "TcoTcoOfferAvailableAt",
                    "variables": {
                        "offerIdentifier": offer_id
                    },
                    "query": "query TcoTcoOfferAvailableAt($offerIdentifier: ID!) {\n  tcoOffer(offerIdentifier: $offerIdentifier) {\n    id\n    offerValueAvailableAt\n    expirationDate\n    vehicle {\n      imageUrl\n      style {\n        id\n        model {\n          id\n          name\n          year\n          make {\n            id\n            name\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
            )

            offer_availability_timepoint = datetime.fromisoformat(offer_availability_response.json()['data']['tcoOffer']['offerValueAvailableAt'])

            while True:
                now = datetime.now(timezone.utc)
                if now > offer_availability_timepoint:
                    break

                time.sleep((offer_availability_timepoint - now).total_seconds())

            offer = None
            while True:
                offer_response = yield scrapy.http.JsonRequest(
                    method='POST',
                    url='https://www.truecar.com/abp/api/graphql/',
                    headers={
                        # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                        "content-type": "application/json",
                        "apollographql-client-name": "abp-frontend",
                        "authorization-mode": "consumer",
                        # "Content-Length": "938",
                        "Origin": "https://www.truecar.com",
                        "Connection": "keep-alive",
                        # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NTIwMzksImV4cCI6MTcxMTk1MjAzOSwianRpIjoiZGJhZTY5ZTktNDQ4MC00ZWNlLWExMWItM2VmYTlkZTYwMjU3IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=msfl83te-bApW5nCXSurpbF1zRrTQejzYSsP3akRl6k; tc_v=a5edad89-eb4a-42f5-a2f2-648976ee86d9; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWLKdiFAARJjjiAg==; utag_main=v_id:018ade9e7c1d0020ed081dd17a2c05046002600900bd0$_sn:1$_se:69$_ss:0$_st:1695953937317$ses_id:1695952043038%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:67%3Bexp-session$dc_region:us-east-1%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T01:47:25.205Z; _dd_s=rum=0&expire=1695953033342; _ga_XD4TBVCD03=GS1.1.1695952048.1.1.1695952136.0.0.0; _ga=GA1.2.1378133854.1695952049; _ga_J3VWL05G5K=GS1.1.1695952048.1.1.1695952136.0.0.0; _gid=GA1.2.161031154.1695952049; _uetsid=2603fc005e6a11eebec6d56901b57243; _uetvid=26042c105e6a11eea422339ea9543c78; _gcl_au=1.1.178583961.1695952050; _fbp=fb.1.1695952052238.34524161; QSI_HistorySession=https%3A%2F%2Fwww.truecar.com%2Fsell-your-car%2F~1695952052346; session_id=b05fba65-1641-4767-9c66-c74da41f1aeb; sa-user-id=s%253A0-407cfff6-a2e4-5710-5207-fa9a4c860aa6.U0vtju36aRBgNJRhcthlhVLFbt3Ty7zYbYjWSG9y438; sa-user-id-v2=s%253AQHz_9qLkVxBSB_qaTIYKpsA1Qp4.F3s31ibL8BRD3eYiNBcRtzNNEw%252BR79NALy5TpEy1sNo; sa-user-id-v3=s%253AAQAKIC5dWB75mTJ0VyPAX4yofM4bcGpf5TJlwMiyGcLgSf0bEK8BGAQgtdnYqAYwAToEC5i6o0IE0NwCiQ.8if83sAuf%252Fq1QyEPcUxCzV8HUTOMemta5cAUvAUwnCU; fs_lua=1.1695952054424; fs_uid=#G5Y78#c4f8a9de-231b-47ef-a55d-4daf38b2ab8b:ef44c37a-a4fb-48fc-81df-20030499f1cc:1695952054424::1#e10b6c4c#/1727488050",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "TE": "trailers"
                    },
                    data={
                        "operationName": "TcoTcoOffer",
                        "variables": {
                            "offerIdentifier": offer_id
                        },
                        "query": "query TcoTcoOffer($offerIdentifier: ID!) {\n  tcoOffer(offerIdentifier: $offerIdentifier) {\n    dealerships {\n      databaseId\n      name\n      id\n      __typename\n    }\n    offerValueGated\n    status\n    value\n    winningVendorDetails {\n      vendorName\n      __typename\n    }\n    vehicle {\n      vin\n      licensePlateNumber\n      imageUrl\n      postalCode\n      conditions {\n        payoffAmount\n        __typename\n      }\n      style {\n        id\n        model {\n          id\n          name\n          year\n          make {\n            id\n            name\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      interiorColor\n      exteriorColor\n      __typename\n    }\n    tcoOfferId\n    id\n    expirationDate\n    __typename\n  }\n}\n"
                    },
                )

                offer = offer_response.json()['data']['tcoOffer']

                if offer['status'] == 'PENDING':
                    time.sleep(3)

                else:
                    break

            if offer['status'] == 'INCOMPLETE':
                raise CantMakeOfferForVin(needs_to_see_vehicle=False)

            elif offer.get('offerValueGated', True):
                winning_vendor = offer['winningVendorDetails']["vendorName"]

                if winning_vendor == "ProgrammaticBidding":
                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "560",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1OWQxZjUwNi1iNWM0LTQ4ZTctODU3YS04ZDIzZDQ1ZTc1YTYiLCJpYXQiOjE2OTU5NjU2MjIsImV4cCI6MTcxMTk2NTYyMiwianRpIjoiYTQ0NTJjNDgtNTE1Mi00ODUzLThjYjYtNmZhMjJjMGJjMzI4IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=cvrf6VOlw9Wy6vs9eP8DN5UGa_xPk56mAUy2e6Co_yg; tc_v=1ac630c6-72dc-4953-b0f7-6dae243a2c9a; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEAFWUWYbYHxQARKCTuAg==; utag_main=v_id:018adf6dbe37001f4b72c88386e305046002600900bd0$_sn:1$_se:72$_ss:0$_st:1695967662084$ses_id:1695965625912%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:70%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T05:33:47.184Z; _dd_s=rum=0&expire=1695966762014; _ga_XD4TBVCD03=GS1.1.1695965629.1.1.1695965705.0.0.0; _ga=GA1.1.1819299279.1695965629; _ga_J3VWL05G5K=GS1.1.1695965629.1.1.1695965705.0.0.0; _gcl_au=1.1.765550331.1695965630; session_id=e514aca6-0ace-4681-8bb6-9081d68ef198",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "advanceTrueCashOffer",
                            "variables": {
                                "input": {
                                    "offerIdentifier": offer_id,
                                    "firstName": result['first_name'],
                                    "lastName": result['last_name'],
                                    "phoneNumber": result['phone_number'],
                                    "emailAddress": result['email'],
                                    "postalCode": result['zip_code'],
                                    "preferredContactMethod": "ANY"
                                }
                            },
                            "query": "mutation advanceTrueCashOffer($input: AdvanceTrueCashOfferInput!) {\n  advanceTrueCashOffer(input: $input) {\n    tcoOffer {\n      id\n      dealerships {\n        name\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    advanced_offer = yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "497",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1OWQxZjUwNi1iNWM0LTQ4ZTctODU3YS04ZDIzZDQ1ZTc1YTYiLCJpYXQiOjE2OTU5NjU2MjIsImV4cCI6MTcxMTk2NTYyMiwianRpIjoiYTQ0NTJjNDgtNTE1Mi00ODUzLThjYjYtNmZhMjJjMGJjMzI4IiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=cvrf6VOlw9Wy6vs9eP8DN5UGa_xPk56mAUy2e6Co_yg; tc_v=1ac630c6-72dc-4953-b0f7-6dae243a2c9a; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEAFWUWYbYHxQARKCTuAg==; utag_main=v_id:018adf6dbe37001f4b72c88386e305046002600900bd0$_sn:1$_se:73$_ss:0$_st:1695967663962$ses_id:1695965625912%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:71%3Bexp-session; tealium_test_field=Test_B; sessionStartTime=2023-09-29T05:33:47.184Z; _dd_s=rum=0&expire=1695966764050; _ga_XD4TBVCD03=GS1.1.1695965629.1.1.1695965863.0.0.0; _ga=GA1.1.1819299279.1695965629; _ga_J3VWL05G5K=GS1.1.1695965629.1.1.1695965863.0.0.0; _gcl_au=1.1.765550331.1695965630; session_id=e514aca6-0ace-4681-8bb6-9081d68ef198",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "TcoAdvanceOffer",
                            "variables": {
                                "offerIdentifier": offer_id
                            },
                            "query": "query TcoAdvanceOffer($offerIdentifier: ID!) {\n  tcoOffer(offerIdentifier: $offerIdentifier) {\n    expirationDate\n    value\n    status\n    id\n    vehicle {\n      imageUrl\n      postalCode\n      conditions {\n        payoffAmount\n        __typename\n      }\n      __typename\n    }\n    consumer {\n      id\n      uuid\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    offer = advanced_offer.json()['data']['tcoOffer']
                    break

                elif winning_vendor == "Peddle":
                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "309",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MmZjOTBlMS02ZTVmLTQwNjAtOGIwNC0wZTczN2MxOTY0MGQiLCJpYXQiOjE2OTU5NzIyNTYsImV4cCI6MTcxMTk3MjI1NiwianRpIjoiYzVkZDMxMTktN2M1NS00Y2QwLTkwNTgtY2U4ZDA3N2YxMDMwIiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=wZaw1dj0Fs6RRWD8nnWgtKT4Ah2O1EUHWkoyAZO5SKU; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:71$_ss:0$_st:1695974137024$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:69%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973254168; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useConsumer_validateEmail",
                            "variables": {
                                "emailAddress": random_account.email
                            },
                            "query": "query useConsumer_validateEmail($emailAddress: String!) {\n  consumerValidateEmail(emailAddress: $emailAddress) {\n    prospected\n    account\n    domain\n    format\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "735",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MmZjOTBlMS02ZTVmLTQwNjAtOGIwNC0wZTczN2MxOTY0MGQiLCJpYXQiOjE2OTU5NzIyNTYsImV4cCI6MTcxMTk3MjI1NiwianRpIjoiYzVkZDMxMTktN2M1NS00Y2QwLTkwNTgtY2U4ZDA3N2YxMDMwIiwiYXV0aGVudGljYXRlZCI6ZmFsc2UsInByZXNldCI6eyJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=wZaw1dj0Fs6RRWD8nnWgtKT4Ah2O1EUHWkoyAZO5SKU; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:72$_ss:0$_st:1695974155714$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:70%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973261150; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useConsumer_signIn",
                            "variables": {
                                "email": random_account.email,
                                "password": random_account.password
                            },
                            "query": "mutation useConsumer_signIn($email: String!, $password: String!) {\n  consumerSignIn(input: {emailAddress: $email, password: $password}) {\n    consumer {\n      id\n      acceptedTos\n      authenticated\n      databaseId\n      uuid\n      verified\n      profile {\n        id\n        emailAddress\n        firstName\n        lastName\n        phoneNumber\n        street1\n        street2\n        city\n        state\n        postalCode\n        preferredPaymentMethod\n        preferredContactMethod\n        __typename\n      }\n      registrationType\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "1601",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNjIsImV4cCI6MTcxMTk3MjM2MiwianRpIjoiNDU4NjBhY2QtNjU5OC00NDViLWE3ZGUtMThjMDcwZjJmNmU4IiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiMDcwMjQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=ELO4XzqX_8X5ywWAS4r5X4MP3hvu4rOv8gu60U0KOnY; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:73$_ss:0$_st:1695974164021$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:71%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973265196; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=TUhjMk5rbkFNcmcyL2dkblJoUFg2WldKY1VxTHRVRG5BVTdwdDJOUjd4dTlZVHNLVTZvUDRhRTM3c1RoL080S1BpWkhHTlMvRHc3R1NXdWg0V0toT3c9PS0tdDhQYU9xWlRzSkU2S2FnOUlxak5KUT09--d399aca5d4fa5dc11adc0b7d8fad27bcd3a84714",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useConsumer_ConsumerUpdate",
                            "variables": {
                                "firstName": random_account.first_name,
                                "lastName": random_account.last_name
                            },
                            "query": "mutation useConsumer_ConsumerUpdate($emailAddress: String, $password: String, $firstName: String, $lastName: String, $phoneNumber: String, $phoneType: String, $street1: String, $street2: String, $city: String, $state: String, $postalCode: String, $comments: String, $purchaseTimeFrame: String, $preferredPaymentMethod: PaymentMethodEnum, $preferredContactMethod: ContactMethodEnum, $acceptedTos: Boolean, $context: UpdateProfileContextEnum) {\n  consumerUpdate(input: {emailAddress: $emailAddress, password: $password, firstName: $firstName, lastName: $lastName, phoneNumber: $phoneNumber, phoneType: $phoneType, street1: $street1, street2: $street2, city: $city, state: $state, postalCode: $postalCode, comments: $comments, purchaseTimeFrame: $purchaseTimeFrame, preferredPaymentMethod: $preferredPaymentMethod, preferredContactMethod: $preferredContactMethod, acceptedTos: $acceptedTos, context: $context}) {\n    consumer {\n      id\n      acceptedTos\n      authenticated\n      databaseId\n      uuid\n      verified\n      profile {\n        id\n        emailAddress\n        firstName\n        lastName\n        phoneNumber\n        street1\n        street2\n        city\n        state\n        postalCode\n        preferredPaymentMethod\n        preferredContactMethod\n        __typename\n      }\n      registrationType\n      __typename\n    }\n    consumerErrors {\n      ... on ConsumerError {\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "279",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNjUsImV4cCI6MTcxMTk3MjM2NSwianRpIjoiNGZhZjIyNzctOWUzNy00ODQ1LThjOTItNzcxZmIyN2ViYTI5IiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiMDcwMjQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=THunFg_nc6VsQ3RVQzW9ABupykAimLmPkCxnYzguReo; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:73$_ss:0$_st:1695974164021$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:71%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973266306; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=elFhY0F0K3RpMU1wRTFUOGhEUHExRUU0a2U0ZkZRRjF0Y0xBZkdwMklhMTVzM3pDWWtOVWVSK25YVldtdnR0MkZXYWRhZXE3dysrZlVEWW5rVldETVE9PS0tUW5nOGpOWWNjVG45T3Z2SUpTT0RVdz09--704ee82a22863b178d6881a92e9787d55d7e6783",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useGeolocation",
                            "variables": {
                                "postalCode": random_account.zip_code
                            },
                            "query": "query useGeolocation($postalCode: String!) {\n  geolocation(postalCode: $postalCode) {\n    id\n    postalCode\n    city\n    citySlug\n    state\n    stateSlug\n    isPoBox\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "1636",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNjUsImV4cCI6MTcxMTk3MjM2NSwianRpIjoiNGZhZjIyNzctOWUzNy00ODQ1LThjOTItNzcxZmIyN2ViYTI5IiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiMDcwMjQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=THunFg_nc6VsQ3RVQzW9ABupykAimLmPkCxnYzguReo; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:74$_ss:0$_st:1695974166309$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:72%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973267662; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=b2txdW9hSG51VEJOcWhNd1hMSCtLUlpWRUpWU3drVG50aUxlY3cxWmZGVm5lKzF4amZ6QWhUeURVKzhPUVEwTk5uakN0YldzdjAxVHpGNEN0S1BqZ1E9PS0tc3QyY00wNUFFcTJpNGRqeDJjaFY0UT09--1bc01e7d15322addb36ce5b5a5a8dde943d7e0ca; capselaPreferredPostalCode=90404",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useConsumer_ConsumerUpdate",
                            "variables": {
                                "postalCode": random_account.zip_code,
                                "street1": random_account.street_address,
                                "street2": ""
                            },
                            "query": "mutation useConsumer_ConsumerUpdate($emailAddress: String, $password: String, $firstName: String, $lastName: String, $phoneNumber: String, $phoneType: String, $street1: String, $street2: String, $city: String, $state: String, $postalCode: String, $comments: String, $purchaseTimeFrame: String, $preferredPaymentMethod: PaymentMethodEnum, $preferredContactMethod: ContactMethodEnum, $acceptedTos: Boolean, $context: UpdateProfileContextEnum) {\n  consumerUpdate(input: {emailAddress: $emailAddress, password: $password, firstName: $firstName, lastName: $lastName, phoneNumber: $phoneNumber, phoneType: $phoneType, street1: $street1, street2: $street2, city: $city, state: $state, postalCode: $postalCode, comments: $comments, purchaseTimeFrame: $purchaseTimeFrame, preferredPaymentMethod: $preferredPaymentMethod, preferredContactMethod: $preferredContactMethod, acceptedTos: $acceptedTos, context: $context}) {\n    consumer {\n      id\n      acceptedTos\n      authenticated\n      databaseId\n      uuid\n      verified\n      profile {\n        id\n        emailAddress\n        firstName\n        lastName\n        phoneNumber\n        street1\n        street2\n        city\n        state\n        postalCode\n        preferredPaymentMethod\n        preferredContactMethod\n        __typename\n      }\n      registrationType\n      __typename\n    }\n    consumerErrors {\n      ... on ConsumerError {\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "280",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNjgsImV4cCI6MTcxMTk3MjM2OCwianRpIjoiY2Q4OWRhNTktYjcxNi00NjcyLWJkMDctMDZiMjNjZGE1YjcxIiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiOTA0MDQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=rcFvbNX4SnYjWuHG5ibJnOyoRg8I-xHLYhPpGdDtMOo; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:76$_ss:0$_st:1695974169770$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:74%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973270787; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=TjAzNk9JSlVuMnNOVGhpcVYwbXI3Q0hWcmtCSjlxQkR3L1hHOUUrU0ticTlPUnVaOWJVQ0hKZzkzd2ErNHNrUU1yYlVqRDNZZlJKRmMzcmM5OGUxbGc9PS0tYSs2azBqRkFRU2p3ZVZmTi9QeUo2dz09--2549eddf066bfb696e11e3480c06db40af2d3afd; capselaPreferredPostalCode=90404",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "formPhoneNumber",
                            "variables": {
                                "phoneNumber": random_account.phone_number
                            },
                            "query": "query formPhoneNumber($phoneNumber: String!) {\n  phoneNumber(phoneNumber: $phoneNumber) {\n    validation {\n      result\n      messages\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "1640",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNjgsImV4cCI6MTcxMTk3MjM2OCwianRpIjoiY2Q4OWRhNTktYjcxNi00NjcyLWJkMDctMDZiMjNjZGE1YjcxIiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiOTA0MDQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=rcFvbNX4SnYjWuHG5ibJnOyoRg8I-xHLYhPpGdDtMOo; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:76$_ss:0$_st:1695974169770$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:74%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973270787; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=Z3dTaXlyQ0FPLzVYT0tpWHU1VHM1QUpiSUwzQXgvaTZqRk1rYlo3VGtqZUVzVVBtc2FFSjV3eS82T2lrK0JHc0pCVTNEQjNyeURmMUFkZmVwT3RKblE9PS0tVi9yS0I0KzMveEZsL2c5SldITlN6dz09--f8b2f8001f67dcb0de7f43495f5e8938dc216040; capselaPreferredPostalCode=90404",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "useConsumer_ConsumerUpdate",
                            "variables": {
                                "phoneNumber": random_account.phone_number,
                                "preferredContactMethod": "ANY",
                                "acceptedTos": True
                            },
                            "query": "mutation useConsumer_ConsumerUpdate($emailAddress: String, $password: String, $firstName: String, $lastName: String, $phoneNumber: String, $phoneType: String, $street1: String, $street2: String, $city: String, $state: String, $postalCode: String, $comments: String, $purchaseTimeFrame: String, $preferredPaymentMethod: PaymentMethodEnum, $preferredContactMethod: ContactMethodEnum, $acceptedTos: Boolean, $context: UpdateProfileContextEnum) {\n  consumerUpdate(input: {emailAddress: $emailAddress, password: $password, firstName: $firstName, lastName: $lastName, phoneNumber: $phoneNumber, phoneType: $phoneType, street1: $street1, street2: $street2, city: $city, state: $state, postalCode: $postalCode, comments: $comments, purchaseTimeFrame: $purchaseTimeFrame, preferredPaymentMethod: $preferredPaymentMethod, preferredContactMethod: $preferredContactMethod, acceptedTos: $acceptedTos, context: $context}) {\n    consumer {\n      id\n      acceptedTos\n      authenticated\n      databaseId\n      uuid\n      verified\n      profile {\n        id\n        emailAddress\n        firstName\n        lastName\n        phoneNumber\n        street1\n        street2\n        city\n        state\n        postalCode\n        preferredPaymentMethod\n        preferredContactMethod\n        __typename\n      }\n      registrationType\n      __typename\n    }\n    consumerErrors {\n      ... on ConsumerError {\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    peddle_offer = yield scrapy.http.JsonRequest(
                        method='POST',
                        url='https://www.truecar.com/abp/api/graphql/',
                        headers={
                            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br",
                            "referer": f"https://www.truecar.com/trade/dashboard/{offer_id}/",
                            "content-type": "application/json",
                            "apollographql-client-name": "abp-frontend",
                            "authorization-mode": "consumer",
                            # "Content-Length": "450",
                            "Origin": "https://www.truecar.com",
                            "DNT": "1",
                            "Connection": "keep-alive",
                            # "Cookie": "tcip=192.53.66.158; tcPlusServiceArea=no; flag-trade-partner=true; referrer=ZTC0000000; _abp_auth_p=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMjhkZjQzMS02M2E2LTQxODYtOGFkYy1iNjAxMzQ0YzJkOTUiLCJpYXQiOjE2OTU5NzIzNzIsImV4cCI6MTcxMTk3MjM3MiwianRpIjoiM2VkZTE0MmQtYjU5Ny00ZDYwLTgzY2EtNDNiZTViYWQ5NmRmIiwiYXV0aGVudGljYXRlZCI6dHJ1ZSwicHJlc2V0Ijp7ImZpcnN0X25hbWUiOiJBc2hsZWlnaCIsImxhc3RfbmFtZSI6IkRveWxlIiwiZW1haWwiOiJrLmFwLnUucm8ua2l2LmkubmNlQGdtYWlsLmNvbSIsInBvc3RhbF9jb2RlIjoiOTA0MDQiLCJhZmZpbGlhdGlvbnMiOltdfSwiYXVkIjoiaHR0cHM6Ly93d3cudHJ1ZWNhci5jb20ifQ; _abp_auth_s=iD3nEv47Doa3-o6wpyDT7NXp5P53pDfqc9Ucfh-bZCY; tc_v=740e0982-70e0-4841-a521-d63d8c498271; flag-abt-ev-hub-hyundai-ioniq-6=true; militaryServiceArea=no; u=rBEACmUWe6BiFAARKUdWAg==; utag_main=v_id:018adfd301d70021d9243bc659fc05046002600900bd0$_sn:1$_se:76$_ss:0$_st:1695974169770$ses_id:1695972262360%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:74%3Bexp-session; tealium_test_field=Test_C; sessionStartTime=2023-09-29T07:24:23.916Z; _dd_s=rum=0&expire=1695973270787; _ga_XD4TBVCD03=GS1.1.1695972267.1.1.1695972337.0.0.0; _ga=GA1.1.892665180.1695972267; _ga_J3VWL05G5K=GS1.1.1695972267.1.1.1695972337.0.0.0; session_id=38e3db5a-5a4a-4a61-b70f-ba4fbd3b6496; _gcl_au=1.1.910095537.1695972274; _abp_backend_session=bGtnTDRTTGdhemtoYUhmNlVKTEM4S0liV1F2UGwvd25PbEFnRGVsbStWRFBxUmpGUEUxV0xDenN2Rm9pYWQ2UlFzbEFTS0lpN0RFbjdjYlZwY0swS2c9PS0tZ29seGFOcVloNjlybU9NaEcyY1pGQT09--3b4cbde5926da4283adfab9109d840aa61f66fa1; capselaPreferredPostalCode=90404",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "TE": "trailers"
                        },
                        data={
                            "operationName": "advancePeddleOffer",
                            "variables": {
                                "input": {
                                    "offerIdentifier": offer_id
                                }
                            },
                            "query": "mutation advancePeddleOffer($input: AdvancePeddleOfferInput!) {\n  advancePeddleOffer(input: $input) {\n    tcoErrors {\n      __typename\n    }\n    peddleReferenceId\n    tcoOffer {\n      id\n      dealerships {\n        name\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                    )

                    if len(peddle_offer.json()['data']['advancePeddleOffer']['tcoErrors']):
                        raise OfferAlreadyExists

                else:
                    raise UnknownDealer

            elif not offer['value']:
                raise ProxyBlocked()

            else:
                break

        price = float(offer['value'])
        result['price'] = price

        yield result
