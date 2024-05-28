import time
import scrapy
from car_prices.spiders.basic import basic_spider


class OptionsCargurusSpider(basic_spider(source='Cargurus', category='options')):
    def process_requests(self, result):
        make_models_response = yield scrapy.FormRequest(
            method='GET',
            url='https://www.cargurus.com/Cars/getCarPickerReferenceDataAJAX.action',
            headers={
                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cargurus.com/Cars/car-valuation",
                "X-Requested-With": "XMLHttpRequest",
                # "DNT": "1",
                # "Connection": "keep-alive",
                # "Cookie": "JSESSIONID=B2A12C601F27ABDB84A769E5E985DC9E.67dde; ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=n7D6-192.53.67.152.1684383612952; cg-ssid=b1f59f2e330cd2065aa0dd22046cd0d25509c7382af2798dbd05b9b18b407e30; MultivariateTest=H4sIAAAAAAAAAE2QSw7CMAxE7%2BI1SI6%2FSVlXgITYcJyqdyd2IenuaTQz8WSD9X1%2FPT8PWDYgc1jgWuAC5NwRbxhcMdk6M4XFq4aOrbM0CRYeUat%2FtKNEM2jDUGvKwTOldTzIRaaBcOpMQ6emk71M1mBD6lyET57ImrbsOY1rRyenjvNe9GTJG45%2BSn%2BM9v4NMUR%2B%2Br5%2FASCpSndJAQAAHTo2QRbCc0wtxLTa5cFI40TeZi2uLww4EErVqzHwTXA%3D; LSW=www-i-0f7ee82791d589a75; datadome=26tFDzJY3QgBBSnnzwT0b8nIdvjie61jqain7A5Dw7-T8Y32t-ejlTvs01ROsK-cxbjxSNT0bCQrFf0m6TYh0MHfJWLt5dL23PD18Qjp~imNE5Ee6iBIX9j_px8zGc0r; usprivacy=1YNN",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "trailers"
            },
            formdata={
                'forPriceAnalysis': 'true',
                'showInactive': 'false',
                'newCarsOnly': 'false',
                'useInventoryService': 'true',
                'quotableCarsOnly': 'false',
                'carsWithRegressionOnly': 'false',
                'localeCountryCarsOnly': 'true',
                'isResearch': 'false',
            },
        )

        make_models = {make: [model_info for model_info in (make_info.get('popular', []) + make_info.get(
            'unpopular', []))] for make, make_info in make_models_response.json()['allMakerModels'].items()}

        result['vehicles'] = {}

        for make in make_models:
            result['vehicles'][make] = {}

            for model_info in make_models[make]:
                model = model_info['modelName']
                model_id = model_info['modelId']

                result['vehicles'][make][model] = {}

                trims_response = yield scrapy.FormRequest(
                    method='GET',
                    url='https://www.cargurus.com/Cars/getSelectedModelCarTrimsAJAX.action',
                    headers={
                        # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Referer": "https://www.cargurus.com/Cars/car-valuation",
                        "X-Requested-With": "XMLHttpRequest",
                        # "DNT": "1",
                        # "Connection": "keep-alive",
                        # "Cookie": "JSESSIONID=B2A12C601F27ABDB84A769E5E985DC9E.67dde; ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=n7D6-192.53.67.152.1684383612952; cg-ssid=b1f59f2e330cd2065aa0dd22046cd0d25509c7382af2798dbd05b9b18b407e30; MultivariateTest=H4sIAAAAAAAAAE2QSw7CMAxE7%2BI1SI6%2FSVlXgITYcJyqdyd2IenuaTQz8WSD9X1%2FPT8PWDYgc1jgWuAC5NwRbxhcMdk6M4XFq4aOrbM0CRYeUat%2FtKNEM2jDUGvKwTOldTzIRaaBcOpMQ6emk71M1mBD6lyET57ImrbsOY1rRyenjvNe9GTJG45%2BSn%2BM9v4NMUR%2B%2Br5%2FASCpSndJAQAAHTo2QRbCc0wtxLTa5cFI40TeZi2uLww4EErVqzHwTXA%3D; LSW=www-i-0f7ee82791d589a75; datadome=J3nWrr6wNHORZuTPLVvktJxI3N3imqelbphYfY3LgsA_-NndVA8OdJ5aoPs_FEuWHCY2HWFmyVRGtvkGB2-LBXrlZmz20omErDNp5jrmqG-gsNWDkYLnVwCtqL7wr-8; usprivacy=1YNN; _sp_ses.df9a=*; _sp_id.df9a=b38554d6-e08e-44d8-a593-2ca0d4911ce1.1684383620.1.1684383630.1684383620.78cef240-a5a1-4e7f-8567-f6cb0e5e812f; _gcl_au=1.1.156366601.1684383620; _uetsid=4d4c5400f53311edb7058df801914fb7; _uetvid=4d4c4aa0f53311ed89aedb6338be3a71; _ga_0QS2LC2KDY=GS1.1.1684383621.1.1.1684383621.60.0.0; _ga=GA1.1.68537952.1684383621; _td=513430f8-9011-449f-a9df-b995d2643812; FPLC=J03f9gjI1ccYXxCaPsj1AuxYlRYQ5ZDY8XKRGMzdDfvxjEDeBu00pNgcdrjdhLOeSzUcm%2FB1ujT%2FdAl9PGHIdWFsUY2BT1XHXrMuNVOUfMj7E%2BZc1DAyHQVKZUCVNg%3D%3D; FPID=FPID2.2.30xowWJURSJAPAbGCrWdQyrR3sBoCepqMi3PyN2LR0g%3D.1684383621; sp-nuid=a695d4ab-d63a-4135-8d42-21ad3c7c1975",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "TE": "trailers"
                    },
                    formdata={
                        'model': model_id,
                        'forPriceAnalysis': 'true',
                        'showInactive': 'false',
                        'newCarsOnly': 'false',
                        'useInventoryService': 'true',
                        'quotableCarsOnly': 'false',
                        'carsWithRegressionOnly': 'false',
                        'localeCountryCarsOnly': 'true',
                        'isResearch': 'false',
                    },
                )

                for trim_info in (trim for year in trims_response.json().values() for trim in (year['eligibleTrims'] + year['ineligibleTrims'])):
                    trim = trim_info['trimName']
                    trim_id = trim_info['trimId']

                    if trim not in result['vehicles'][make][model]:
                        result['vehicles'][make][model][trim] = {}

                        transmissions_response = yield scrapy.FormRequest(
                            method='GET',
                            url='https://www.cargurus.com/Cars/transmissionListTrimFirst.action',
                            headers={
                                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                                "Accept": "text/html, */*; q=0.01",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Referer": "https://www.cargurus.com/Cars/car-valuation",
                                "X-Requested-With": "XMLHttpRequest",
                                # "DNT": "1",
                                # "Connection": "keep-alive",
                                # "Cookie": "JSESSIONID=B2A12C601F27ABDB84A769E5E985DC9E.67dde; ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=n7D6-192.53.67.152.1684383612952; cg-ssid=b1f59f2e330cd2065aa0dd22046cd0d25509c7382af2798dbd05b9b18b407e30; MultivariateTest=H4sIAAAAAAAAAE2QSw7CMAxE7%2BI1SI6%2FSVlXgITYcJyqdyd2IenuaTQz8WSD9X1%2FPT8PWDYgc1jgWuAC5NwRbxhcMdk6M4XFq4aOrbM0CRYeUat%2FtKNEM2jDUGvKwTOldTzIRaaBcOpMQ6emk71M1mBD6lyET57ImrbsOY1rRyenjvNe9GTJG45%2BSn%2BM9v4NMUR%2B%2Br5%2FASCpSndJAQAAHTo2QRbCc0wtxLTa5cFI40TeZi2uLww4EErVqzHwTXA%3D; LSW=www-i-0f7ee82791d589a75; datadome=J3nWrr6wNHORZuTPLVvktJxI3N3imqelbphYfY3LgsA_-NndVA8OdJ5aoPs_FEuWHCY2HWFmyVRGtvkGB2-LBXrlZmz20omErDNp5jrmqG-gsNWDkYLnVwCtqL7wr-8; usprivacy=1YNN; _sp_id.df9a=b38554d6-e08e-44d8-a593-2ca0d4911ce1.1684383620.2.1684387049.1684383640.8220905c-540a-4095-b12e-704c437c45cf; _gcl_au=1.1.156366601.1684383620; _uetsid=4d4c5400f53311edb7058df801914fb7; _uetvid=4d4c4aa0f53311ed89aedb6338be3a71; _ga_0QS2LC2KDY=GS1.1.1684383621.1.1.1684383621.60.0.0; _ga=GA1.1.68537952.1684383621; _td=513430f8-9011-449f-a9df-b995d2643812; FPLC=J03f9gjI1ccYXxCaPsj1AuxYlRYQ5ZDY8XKRGMzdDfvxjEDeBu00pNgcdrjdhLOeSzUcm%2FB1ujT%2FdAl9PGHIdWFsUY2BT1XHXrMuNVOUfMj7E%2BZc1DAyHQVKZUCVNg%3D%3D; FPID=FPID2.2.30xowWJURSJAPAbGCrWdQyrR3sBoCepqMi3PyN2LR0g%3D.1684383621; sp-nuid=a695d4ab-d63a-4135-8d42-21ad3c7c1975; _sp_ses.df9a=*; mySavedListings=%7B%22id%22%3A%22dd479da8-d2cb-4e18-af23-efdbefc938e0%22%7D",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin",
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "TE": "trailers"
                            },
                            formdata={
                                'trim': trim_id,
                            }
                        )

                        transmissions_text = transmissions_response.text
                        if transmissions_text:
                            transmissions = [value for keyword, value in (element.split(
                                '=') for element in transmissions_text.split(';')) if keyword != 'GroupLabel']
                            result['vehicles'][make][model][trim]['transmissions'] = transmissions

                        engines_response = yield scrapy.FormRequest(
                            method='GET',
                            url='https://www.cargurus.com/Cars/getEngineList.action',
                            headers={
                                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Referer": "https://www.cargurus.com/Cars/car-valuation",
                                "X-Requested-With": "XMLHttpRequest",
                                "DNT": "1",
                                "Proxy-Authorization": "Basic Z2lvaWRidW0tMTpiZWRwdGk4eWRqczM=",
                                "Connection": "keep-alive",
                                "Cookie": "JSESSIONID=B2A12C601F27ABDB84A769E5E985DC9E.67dde; ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=n7D6-192.53.67.152.1684383612952; cg-ssid=b1f59f2e330cd2065aa0dd22046cd0d25509c7382af2798dbd05b9b18b407e30; MultivariateTest=H4sIAAAAAAAAAE2QSw7CMAxE7%2BI1SI6%2FSVlXgITYcJyqdyd2IenuaTQz8WSD9X1%2FPT8PWDYgc1jgWuAC5NwRbxhcMdk6M4XFq4aOrbM0CRYeUat%2FtKNEM2jDUGvKwTOldTzIRaaBcOpMQ6emk71M1mBD6lyET57ImrbsOY1rRyenjvNe9GTJG45%2BSn%2BM9v4NMUR%2B%2Br5%2FASCpSndJAQAAHTo2QRbCc0wtxLTa5cFI40TeZi2uLww4EErVqzHwTXA%3D; LSW=www-i-0f7ee82791d589a75; datadome=J3nWrr6wNHORZuTPLVvktJxI3N3imqelbphYfY3LgsA_-NndVA8OdJ5aoPs_FEuWHCY2HWFmyVRGtvkGB2-LBXrlZmz20omErDNp5jrmqG-gsNWDkYLnVwCtqL7wr-8; usprivacy=1YNN; _sp_id.df9a=b38554d6-e08e-44d8-a593-2ca0d4911ce1.1684383620.2.1684387049.1684383640.8220905c-540a-4095-b12e-704c437c45cf; _gcl_au=1.1.156366601.1684383620; _uetsid=4d4c5400f53311edb7058df801914fb7; _uetvid=4d4c4aa0f53311ed89aedb6338be3a71; _ga_0QS2LC2KDY=GS1.1.1684383621.1.1.1684383621.60.0.0; _ga=GA1.1.68537952.1684383621; _td=513430f8-9011-449f-a9df-b995d2643812; FPLC=J03f9gjI1ccYXxCaPsj1AuxYlRYQ5ZDY8XKRGMzdDfvxjEDeBu00pNgcdrjdhLOeSzUcm%2FB1ujT%2FdAl9PGHIdWFsUY2BT1XHXrMuNVOUfMj7E%2BZc1DAyHQVKZUCVNg%3D%3D; FPID=FPID2.2.30xowWJURSJAPAbGCrWdQyrR3sBoCepqMi3PyN2LR0g%3D.1684383621; sp-nuid=a695d4ab-d63a-4135-8d42-21ad3c7c1975; _sp_ses.df9a=*; mySavedListings=%7B%22id%22%3A%22dd479da8-d2cb-4e18-af23-efdbefc938e0%22%7D",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin",
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "TE": "trailers"
                            },
                            formdata={
                                'trim': trim_id,
                            },
                        )

                        result['vehicles'][make][model][trim]['engines'] = [
                            engine['name'] for engine in engines_response.json()]

                        options_response = yield scrapy.FormRequest(
                            method='GET',
                            url='https://www.cargurus.com/Cars/getOptionList.action',
                            headers={
                                # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
                                "Accept": "text/html, */*; q=0.01",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Referer": "https://www.cargurus.com/Cars/car-valuation",
                                "X-Requested-With": "XMLHttpRequest",
                                # "DNT": "1",
                                # "Connection": "keep-alive",
                                # "Cookie": "JSESSIONID=B2A12C601F27ABDB84A769E5E985DC9E.67dde; ViewVersion=%7B%22en%22%3A%7B%22exclude%22%3A%7B%227bf01801-3707-433d-b5c9-35e3ac9fe5b7%22%3A1%7D%2C%22type%22%3A%22OUT%22%7D%7D; CarGurusUserT=n7D6-192.53.67.152.1684383612952; cg-ssid=b1f59f2e330cd2065aa0dd22046cd0d25509c7382af2798dbd05b9b18b407e30; MultivariateTest=H4sIAAAAAAAAAE2QSw7CMAxE7%2BI1SI6%2FSVlXgITYcJyqdyd2IenuaTQz8WSD9X1%2FPT8PWDYgc1jgWuAC5NwRbxhcMdk6M4XFq4aOrbM0CRYeUat%2FtKNEM2jDUGvKwTOldTzIRaaBcOpMQ6emk71M1mBD6lyET57ImrbsOY1rRyenjvNe9GTJG45%2BSn%2BM9v4NMUR%2B%2Br5%2FASCpSndJAQAAHTo2QRbCc0wtxLTa5cFI40TeZi2uLww4EErVqzHwTXA%3D; LSW=www-i-0f7ee82791d589a75; datadome=J3nWrr6wNHORZuTPLVvktJxI3N3imqelbphYfY3LgsA_-NndVA8OdJ5aoPs_FEuWHCY2HWFmyVRGtvkGB2-LBXrlZmz20omErDNp5jrmqG-gsNWDkYLnVwCtqL7wr-8; usprivacy=1YNN; _sp_id.df9a=b38554d6-e08e-44d8-a593-2ca0d4911ce1.1684383620.2.1684387049.1684383640.8220905c-540a-4095-b12e-704c437c45cf; _gcl_au=1.1.156366601.1684383620; _uetsid=4d4c5400f53311edb7058df801914fb7; _uetvid=4d4c4aa0f53311ed89aedb6338be3a71; _ga_0QS2LC2KDY=GS1.1.1684383621.1.1.1684383621.60.0.0; _ga=GA1.1.68537952.1684383621; _td=513430f8-9011-449f-a9df-b995d2643812; FPLC=J03f9gjI1ccYXxCaPsj1AuxYlRYQ5ZDY8XKRGMzdDfvxjEDeBu00pNgcdrjdhLOeSzUcm%2FB1ujT%2FdAl9PGHIdWFsUY2BT1XHXrMuNVOUfMj7E%2BZc1DAyHQVKZUCVNg%3D%3D; FPID=FPID2.2.30xowWJURSJAPAbGCrWdQyrR3sBoCepqMi3PyN2LR0g%3D.1684383621; sp-nuid=a695d4ab-d63a-4135-8d42-21ad3c7c1975; _sp_ses.df9a=*; mySavedListings=%7B%22id%22%3A%22dd479da8-d2cb-4e18-af23-efdbefc938e0%22%7D",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin",
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "TE": "trailers"
                            },
                            formdata={
                                'trim': trim_id,
                            },
                        )

                        options_text = options_response.text
                        if options_text:
                            option_types = [option_type.split(
                                '=', 2)[1] for option_type in options_text.split(';')]
                            options = [labeled_option.split(
                                ':', 2)[1] for option_type in option_types for labeled_option in option_type.split(',')]
                            result['vehicles'][make][model][trim]['options'] = options

            time.sleep(60)

        yield result
