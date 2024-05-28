import scrapy
import scrapy.http
import re, json
from car_prices.spiders.car_prices import car_prices_spider
from requests import Session
requests = Session()
import urllib

class CarPricesCarbrainSpider(car_prices_spider(source='CarBrain')):
    conditions = {
        'bad': 'Rough',
        'moderate': 'Average',
        'good': 'Clean',
        'excellent': 'Outstanding',
    }

    condition_codes = {
        'bad': 'ROUGH',
        'moderate': 'AVERAGE',
        'good': 'CLEAN',
        'excellent': 'OUTSTANDING',
    }

    def answers_to_offer_questions(self):
        return {
            'Vehicle Condition': self.condition,
            'Is there any wheel damage?': 'No',
            'Does the vehicle have key fobs?': 'No',
        }
    def parse_response(self, content):
        d = dict()
        content = content.split('|')
        while content:
            key = content.pop(0)
            if content:
                value = content.pop(0)
            else:
                break
            d[key] = value
        return d

    def process_requests(self, result):
        #response = requests.get('https://carbrain.com/get-an-offer')
        #selector = scrapy.Selector(text=response.text)
        #viewstate = selector.xpath('//input[@name="__VIEWSTATE"]//@value').get()
        #eventval = selector.xpath('//input[@name="__EVENTVALIDATION"]//@value').get()
        #viewstategen = selector.xpath('//input[@name="__VIEWSTATEGENERATOR"]//@value').get()
        result['answers'] = self.answers_to_offer_questions()
        """
        url = 'https://carbrain.com/WebServices/Custom.asmx/IsCorrectZip'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json; charset=utf-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://carbrain.com",
            "DNT": "1",
            "Connection": "keep-alive",
            "Referer": "https://carbrain.com/get-an-offer",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers"
        }

        data = {"zip": str(self.zip_code)}

        zip_code_response = yield scrapy.http.JsonRequest(
            url=url,
            method='POST',
            dont_filter=True,
            headers=headers,
            data=data,
        )
        self.logger.debug(zip_code_response.json())
        zip_code = zip_code_response.json().get("d", {}).get("correctedZip")
        url = 'https://carbrain.com/WebServices/Custom.asmx/GetVinMainInfo'
        data = {"vin": str(self.vin)}
        car_model_details = yield scrapy.http.JsonRequest(
            url=url,
            method='POST',
            dont_filter=True,
            headers=headers,
            data=data
        )
        """
        headers_ch = {
                'authority': 'carbrain.com',
                'accept': '*/*',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',  
                'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
				'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36',
                'x-microsoftajax': 'Delta=true',
                'x-requested-with': 'XMLHttpRequest',
        }
        url = "https://carbrain.com/get-an-offer"
        response_enter = yield scrapy.http.Request(
                url=url,
                method='GET',
                dont_filter=True,
                #cookies=cookies,
                headers=headers_ch,
        )       
        selector = scrapy.Selector(text=response_enter.text)
        viewstate = selector.xpath('//input[@name="__VIEWSTATE"]//@value').get()
        eventval = selector.xpath('//input[@name="__EVENTVALIDATION"]//@value').get()
        viewstategen = selector.xpath('//input[@name="__VIEWSTATEGENERATOR"]//@value').get()
        ssManager_TSSM = urllib.parse.parse_qs(selector.xpath('//link[contains(@href, "/Telerik.Web.UI.WebResource.axd")]//@href').get()).get("_TSM_CombinedScripts_")[0]
        scManager_TSM = urllib.parse.parse_qs(selector.xpath('//script[contains(@src, "scManager_TSM")]//@src').get()).get("_TSM_CombinedScripts_")[0]
        data = {
	        "ctl00$ctl00$scManager": ["ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton"],
	        "ssManager_TSSM": [ssManager_TSSM],
	        "scManager_TSM": [scManager_TSM],
	        "__EVENTTARGET": ["ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton"],
	        "__EVENTARGUMENT": [""],
	        "__VIEWSTATE": [viewstate],
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": [""],
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": ['{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":""}'],
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ZipCodeField": [self.zip_code],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": ["#ZipCode"],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": ["___-___-____"],
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": ['{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":"___-___-____"}'],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": ["___-___-____"],
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": ['{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":"___-___-____"}'],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": [""],
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": [""],
	        "__VIEWSTATEGENERATOR": [viewstategen],
	        "__EVENTVALIDATION": [eventval],
	        "__ASYNCPOST": ["true"],
        }
        response_zipcode = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data,
        )
         
        zipcode_d = self.parse_response(response_zipcode.text)
        viewstate_zip = zipcode_d.get('__VIEWSTATE')
        eventval_zip = zipcode_d.get("__EVENTVALIDATION")
        viewstategen_zip = zipcode_d.get("__VIEWSTATEGENERATOR")
        data_zip = {
                "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
                "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
                "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
                "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VinSelector_FastLane_ClientState": "{\"text\":\"\",\"value\":\"FAST_LANE\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
                "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VinSelector_ScenicRoute_ClientState": "{\"text\":\"\",\"value\":\"SCENIC_ROUTE\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
                "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
                "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
                "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
                "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
                "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
                "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
                "__VIEWSTATE": viewstate_zip,
                "__VIEWSTATEGENERATOR": viewstategen_zip,
                "__EVENTVALIDATION": eventval_zip,
                "__ASYNCPOST": "true",
                "scManager_TSM": scManager_TSM,
            }
        response_fastlane = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_zip,
        )
        fastlane_d = self.parse_response(response_fastlane.text)
        viewstate_fastlane = fastlane_d.get('__VIEWSTATE')
        eventval_fastlane = fastlane_d.get("__EVENTVALIDATION")
        viewstategen_fastlane = fastlane_d.get("__VIEWSTATEGENERATOR")
        data_fastlane = {
                'ctl00$ctl00$scManager': 'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton',
                'scManager_TSM': scManager_TSM,
                'ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":""}',
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1': 'on',
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1': 'on',
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VinField': self.vin,
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField': '#ZipCode',
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField': '___-___-____',
                'ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":"___-___-____"}',
                'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField': '___-___-____',
                'ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"___-___-____","valueWithPromptAndLiterals":"___-___-____","lastSetTextBoxValue":"___-___-____"}',
                '__EVENTTARGET': 'ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton',
                '__VIEWSTATEGENERATOR': viewstategen_fastlane,
                '__EVENTVALIDATION': eventval_fastlane,
                '__VIEWSTATE': viewstate_fastlane,
                '__ASYNCPOST': 'true'
            }
        response_vin = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_fastlane,
        )
        vin_d = self.parse_response(response_vin.text)
        viewstate_vin = vin_d.get('__VIEWSTATE')
        eventval_vin = vin_d.get("__EVENTVALIDATION")
        viewstategen_vin = vin_d.get("__VIEWSTATEGENERATOR")
        data_cleantitle = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_TitleCleanRadio_ClientState": "{\"text\":\"Clean Title\",\"value\":\"CLEAN\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_TitleSalvageRebuildRadio_ClientState": "{\"text\":\"Salvage or Reconstructed/Rebuilt Title\",\"value\":\"SALVAGE_REBUILD\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_TitleDontHaveRadio_ClientState": "{\"text\":\"I don’t have a Title\",\"value\":\"DONT_HAVE\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
            'scManager_TSM': scManager_TSM,
	        "__VIEWSTATE": viewstate_vin,
	        "__VIEWSTATEGENERATOR": viewstategen_vin,
	        "__EVENTVALIDATION": eventval_vin,
	        "__ASYNCPOST": "true",
        }
        response_cleantitle = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_cleantitle,
        )
        cleantitle_d = self.parse_response(response_cleantitle.text)
        viewstate_cleantitle = cleantitle_d.get('__VIEWSTATE')
        eventval_cleantitle = cleantitle_d.get("__EVENTVALIDATION")
        viewstategen_cleantitle = cleantitle_d.get("__VIEWSTATEGENERATOR")
        self.mileage = int(str(result['mileage'])[:2])
        data_mileage = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MileageField": str(self.mileage),
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_MileageField_ClientState": json.dumps({'enabled': True, 'emptyMessage': '', 'validationText': str(self.mileage), 'valueAsString': str(self.mileage), 'minValue': 1, 'maxValue': 999, 'lastSetTextBoxValue': str(self.mileage)}),
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_cleantitle,
	        "__VIEWSTATEGENERATOR": viewstategen_cleantitle,
	        "__EVENTVALIDATION": eventval_cleantitle,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM,
        }
        response_mileage = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_mileage,
        )
        mileage_d = self.parse_response(response_mileage.text)
        viewstate_mileage = mileage_d.get('__VIEWSTATE')
        eventval_mileage = mileage_d.get("__EVENTVALIDATION")
        viewstategen_mileage = mileage_d.get("__VIEWSTATEGENERATOR")
        data_driveability = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl05$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_Drivability_NotStartRadio_ClientState": "{\"text\":\"665\",\"value\":\"NOTSTART_OTHER\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_Drivability_NotDriveRadio_ClientState": "{\"text\":\"666\",\"value\":\"START_NOTOK_OTHER\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_Drivability_StartAndDriveRadio_ClientState": "{\"text\":\"667\",\"value\":\"OK\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_mileage,
	        "__VIEWSTATEGENERATOR": viewstategen_mileage,
	        "__EVENTVALIDATION": eventval_mileage,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM,
        }
        response_driveability = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_driveability,
        )
        driveability_d = self.parse_response(response_driveability.text)
        viewstate_driveability = driveability_d.get('__VIEWSTATE')
        eventval_driveability = driveability_d.get("__EVENTVALIDATION")
        viewstategen_driveability = driveability_d.get("__VIEWSTATEGENERATOR")
        data_isbodydamage = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl05$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl06$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_BodyDamageNoButton_ClientState": "{\"text\":\"No\",\"value\":\"false\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_BodyDamageYesButton_ClientState": "{\"text\":\"Yes\",\"value\":\"true\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_driveability,
	        "__VIEWSTATEGENERATOR": viewstategen_driveability,
	        "__EVENTVALIDATION": eventval_driveability,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM,
        }
        response_isbodydamage = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_isbodydamage,
        )
        isbodydamage_d = self.parse_response(response_isbodydamage.text)
        viewstate_isbodydamage = isbodydamage_d.get('__VIEWSTATE')
        eventval_isbodydamage = isbodydamage_d.get("__EVENTVALIDATION")
        viewstategen_isbodydamage = isbodydamage_d.get("__VIEWSTATEGENERATOR")
        data_mechanical = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl05$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl06$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl07$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_MechanicalDamage_BadEngineRadio_ClientState": "{\"text\":\"672\",\"value\":\"ENGINE\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_MechanicalDamage_TransmissionSlippingRadio_ClientState": "{\"text\":\"673\",\"value\":\"TRANSMISSION\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_MechanicalDamage_OtherIssueRadio_ClientState": "{\"text\":\"674\",\"value\":\"OTHER\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_isbodydamage,
	        "__VIEWSTATEGENERATOR": viewstategen_isbodydamage,
	        "__EVENTVALIDATION": eventval_isbodydamage,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM,
        }
        response_mechanical = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_mechanical,
        )
        mechanical_d = self.parse_response(response_mechanical.text)
        viewstate_mechanical = mechanical_d.get('__VIEWSTATE')
        eventval_mechanical = mechanical_d.get("__EVENTVALIDATION")
        viewstategen_mechanical = mechanical_d.get("__VIEWSTATEGENERATOR")
        data_disassembled = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl05$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl06$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl07$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl08$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_IsDisassembledNoButton_ClientState": "{\"text\":\"No\",\"value\":\"false\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_IsDisassembledYesButton_ClientState": "{\"text\":\"Yes\",\"value\":\"true\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
            "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_mechanical,
	        "__VIEWSTATEGENERATOR": viewstategen_mechanical,
	        "__EVENTVALIDATION": eventval_mechanical,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM,
        }
        response_disassembled = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_disassembled,
        )
        disassembled_d = self.parse_response(response_disassembled.text)
        viewstate_disassembled = disassembled_d.get('__VIEWSTATE')
        eventval_disassembled = disassembled_d.get("__EVENTVALIDATION")
        viewstategen_disassembled = disassembled_d.get("__VIEWSTATEGENERATOR")
        data_isotherdamage = {
	        "ctl00$ctl00$scManager": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$UpdatePanel1|ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_FirstPhoneField": "",
	        "ctl00_ctl00_Cnt_Body_Cnt_TopHeader_element_8030_LoginControl_View_FirstPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_TopHeader$element_8030$LoginControl$View_First_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl01$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl02$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl03$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl04$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl05$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl06$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl07$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl08$chb1": "on",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EditPanelDataRepeater$ctl09$chb1": "on",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_IsOtherDamageNoButton_ClientState": "{\"text\":\"No\",\"value\":\"false\",\"checked\":true,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_IsOtherDamageYesButton_ClientState": "{\"text\":\"Yes\",\"value\":\"true\",\"checked\":false,\"target\":\"\",\"navigateUrl\":\"\",\"commandName\":\"\",\"commandArgument\":\"\",\"autoPostBack\":false,\"selectedToggleStateIndex\":0,\"validationGroup\":null,\"readOnly\":false,\"primary\":false,\"enabled\":true}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$CurrHashField": "#ZipCode",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$ViewHashField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$MNoCACLK": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PopupLV": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferNameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferPhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_EmailOfferPhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$EmailOfferEmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_NameField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_PhoneField": "___-___-____",
	        "ctl00_ctl00_Cnt_Body_Cnt_Content_element_6803_VehicleLocContPopup_PhoneField_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"___-___-____\",\"valueWithPromptAndLiterals\":\"___-___-____\",\"lastSetTextBoxValue\":\"___-___-____\"}",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$VehicleLocContPopup_EmailField": "",
	        "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$PhoneVerificationPopup_DIDField": "",
	        "__EVENTTARGET": "ctl00$ctl00$Cnt_Body$Cnt_Content$element_6803$NextButton",
	        "__EVENTARGUMENT": "",
	        "__VIEWSTATE": viewstate_disassembled,
	        "__VIEWSTATEGENERATOR": viewstategen_disassembled,
	        "__EVENTVALIDATION": eventval_disassembled,
	        "__ASYNCPOST": "true",
            'scManager_TSM': scManager_TSM
        }
        response_isotherdamage = yield scrapy.http.FormRequest(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers_ch,
                formdata=data_isotherdamage,
        )
        clean_offer = "".join(re.findall("_offer(.*)", response_isotherdamage.text))
        clean_offer = clean_offer.replace(";\r", "").replace(" ","").strip()
        offer_type = "".join(re.findall("Type='(.*)?'=", clean_offer))
        offer_price = "".join(re.findall(r"\d+[0-9].[0-9][0-9]", clean_offer))
        #self.logger.debug()
        if offer_price:
            result['price'] = float(offer_price)
            result['type'] = offer_type
        else:
            result['success'] = 'we need to check'
        yield result
