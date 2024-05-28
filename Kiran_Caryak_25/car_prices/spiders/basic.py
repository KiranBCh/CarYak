import scrapy
import scrapy.http
from datetime import datetime, timedelta
import random
import json
import re
import car_prices.mongodb as mongodb
from dataclasses import dataclass, asdict
from typing import Any, Callable, Generator, Optional, Tuple, cast, Union
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from car_prices.exceptions import AccountNeeded, CaptchaFailure, AutoCheckFailed, ContactInfoInUse, CantMakeOfferForVin, OfferAlreadyExists, OfferUnderReview, UnencounteredResponse, GenericTwistedError, InvalidContactInfo, MaxAttemptsReached, ProxyBlocked, ScrapingTimeout, TwistedDNSLookupError, TwistedTunnelError, UnknownDealer, VinNotFound
from car_prices.vehicle_analysis import VehicleAnalyser
from car_prices.captcha import CaptchaSolver
from scrapy.core.downloader.handlers.http11 import TunnelError
import names
from car_prices.config import Config
from car_prices.logging import LogHandler


@dataclass
class ContactInfo:
    first_name: str
    last_name: str
    email: str
    phone_number: str


@dataclass
class Proxy:
    username: str
    password: str
    host: str
    port: int
    full_url: str


@dataclass
class VinDetails:
    kbb_details: dict[str, Any]
    year: int
    make: str
    model: str
    trim: str
    engine: str
    transmission: str
    drivetrain: str
    colour: str
    autocheck_data: dict[str, Any]


Result = dict


@dataclass
class RequestMetadata:
    start_time: datetime
    num_attempts: int
    proxy: Proxy


def basic_spider(source: str, category: str):
    source_input = source
    category_input = category

    class Spider(scrapy.Spider):
        source = source_input
        category = category_input
        name = f'{category}_{source}'.lower()
        email_char_set = re.compile(r'[a-zA-Z0-9\-_.@]+$')
        us_phone_number_pattern = re.compile(r'\+1 (\d{3})-(\d{3})-(\d{4})')

        def get_random_temp_mail_email(self, first_name: str, last_name: str) -> str:
            domain_list = [
                # "pacificwest.com",
                # "ravemail.com",
                # "alumni.com",
                # "madonnafan.com",
                # "religious.com",
                # "activist.com",
                # "photographer.net",
                # "dallasmail.com",
                # "presidency.com",
                # "sanfranmail.com",
                # "brew-master.com",
                # "techie.com",
                # "aircraftmail.com",
                # "bartender.net",
                # "irelandmail.com",
                # "spainmail.com",
                # "rocketship.com",
                # "registerednurses.com",
                # "clubmember.org",
                # "qualityservice.com",
                # "swedenmail.com",
                # "cutey.com",
                # "englandmail.com",
                # "hilarious.com",
                # "mail.com",
                # "snakebite.com",
                # "munich.com",
                # "hot-shot.com",
                # "pacific-ocean.com",
                # "chemist.com",
                # "elvisfan.com",
                # "kissfans.com",
                # "planetmail.net",
                # "coolsite.net",
                # "usa.com",
                # "polandmail.com",
                # "chef.net",
                # "repairman.com",
                # "umpire.com",
                # "discofan.com",
                # "mail-me.com",
                # "engineer.com",
                # "rescueteam.com",
                # "israelmail.com",
                # "toothfairy.com",
                # "computer4u.com",
                # "kittymail.com",
                # "writeme.com",
                # "allergist.com",
                # "insurer.com",
                # "optician.com",
                # "homemail.com",
                # "groupmail.com",
                # "null.net",
                # "keromail.com",
                # "muslim.com",
                # "innocent.com",
                # "ninfan.com",
                # "reggaefan.com",
                # "hairdresser.net",
                # "nycmail.com",
                # "theplate.com",
                # "disposable.com",
                # "mexicomail.com",
                # "toke.com",
                # "socialworker.net",
                # "accountant.com",
                # "tech-center.com",
                # "collector.org",
                # "songwriter.net",
                # "californiamail.com",
                # "consultant.com",
                # "contractor.net",
                # "doglover.com",
                # "australiamail.com",
                # "brazilmail.com",
                # "columnist.com",
                # "germanymail.com",
                # "berlin.com",
                # "cybergal.com",
                # "solution4u.com",
                # "africamail.com",
                # "net-shopping.com",
                # "email.com",
                # "metalfan.com",
                # "bellair.net",
                # "archaeologist.com",
                # "gardener.com",
                # "alumnidirector.com",
                # "surgical.net",
                # "webname.com",
                # "atheist.com",
                # "graphic-designer.com",
                # "instructor.net",
                # "lovecat.com",
                # "artlover.com",
                # "counsellor.com",
                # "humanoid.net",
                # "musician.org",
                # "uymail.com",
                # "petlover.com",
                # "execs.com",
                # "worker.com",
                # "saintly.com",
                # "workmail.com",
                # "dublin.com",
                # "samerica.com",
                # "cyberservices.com",
                # "arcticmail.com",
                # "reincarnate.com",
                # "diplomats.com",
                # "radiologist.net",
                # "koreamail.com",
                # "journalist.com",
                # "adexec.com",
                # "swissmail.com",
                # "instruction.com",
                # "cyber-wizard.com",
                # "pediatrician.com",
                # "disciples.com",
                # "minister.com",
                # "priest.com",
                # "comic.com",
                # "catlover.com",
                # "programmer.net",
                # "publicist.com",
                # "representative.com",
                # "europe.com",
                # "doramail.com",
                # "angelic.com",
                # "moscowmail.com",
                # "realtyagent.com",
                # "tvstar.com",
                # "hiphopfan.com",
                # "geologist.com",
                # "dutchmail.com",
                # "therapist.net",
                # "salesperson.net",
                # "acdcfan.com",
                # "politician.com",
                # "graduate.org",
                # "physicist.net",
                # "technologist.com",
                # "fastservice.com",
                # "orthodontist.net",
                # "post.com",
                # "legislator.com",
                # "planetmail.com",
                # "lobbyist.com",
                # "nonpartisan.com",
                # "bikerider.com",
                # "cyberdude.com",
                # "dbzmail.com",
                # "secretary.net",
                # "boardermail.com",
                # "myself.com",
                # "financier.com",
                # "marchmail.com",
                # "job4u.com",
                # "deliveryman.com",
                # "blader.com",
                # "birdlover.com",
                # "torontomail.com",
                # "protestant.com",
                # "brew-meister.com",
                # "auctioneer.net",
                # "sociologist.com",
                # "linuxmail.org",
                # "asia.com",
                # "bsdmail.com",
                # "iname.com",
                # "hackermail.com",
                # "greenmail.net",
                # "chinamail.com",
                # "galaxyhit.com",
                # "housemail.com",
                # "fireman.net",
                # "safrica.com",
                # "dr.com",
                # "inorbit.com",
                # "teachers.org",
                # "cash4u.com",
                # "cheerful.com",
                # "europemail.com",
                # "reborn.com",
                # "asia-mail.com",
                # "scotlandmail.com",
                # "italymail.com",
                "cevipsa.com",
                "cpav3.com",
                "nuclene.com",
                "steveix.com",
                "mocvn.com",
                "tenvil.com",
                "tgvis.com",
                "amozix.com",
                "anypsd.com",
                "maxric.com",
            ]

            return f"{first_name}.{last_name}{random.randint(99, 999)}@{random.choice(domain_list)}"

        def get_random_database_email(self) -> str:
            return list(self.database.handle['email'].aggregate([{'$sample': {'size': 1}}]))[0]['email'] if self.database else 'su.l.l.i.vanfra.n.4197.7@gmail.com'

        def get_random_email(self) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
            earlist_possible_date = datetime.utcnow() - timedelta(days=30)

            def fetch_email_and_update_database(database: mongodb.Database) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
                while True:
                    random_email_list = list(database.handle['gmailnator_emails'].aggregate([{'$match': {'$or': [{'last_used': None}, {'last_used': {'$lt': earlist_possible_date}}]}}, {'$sample': {'size': 1}}]))

                    if random_email_list:
                        email_doc = random_email_list[0]
                        database.handle['gmailnator_emails'].update_one({'_id': email_doc['_id']}, {'$set': {'last_used': datetime.utcnow()}})

                        return email_doc['email']

                    else:
                        bulk_email_response = yield scrapy.http.JsonRequest(
                            method='POST',
                            url='https://gmailnator.p.rapidapi.com/bulk-emails',
                            headers={
                                "X-RapidAPI-Host": "gmailnator.p.rapidapi.com",
                                "X-RapidAPI-Key": self.config.rapid_api.key,
                                "content-type": "application/json"
                            },
                            data={
                                'limit': 500,
                                'options': [3],
                            }
                        )
                        emails = cast(list[str], bulk_email_response.json())

                        database.handle['gmailnator_emails'].insert_many(({'email': email, 'last_used': None} for email in emails))

            return (yield from fetch_email_and_update_database(self.database)) if self.database else 'su.l.l.i.vanfra.n.4197.7@gmail.com'

        def get_random_disposable_gmail_email(self) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
            try:
                while True:
                    email_response = yield scrapy.Request(
                        method='GET',
                        url='https://disposable-gmail.p.rapidapi.com/generate',
                        headers={
                            "X-RapidAPI-Host": "disposable-gmail.p.rapidapi.com",
                            "X-RapidAPI-Key": self.config.disposable_gmail.key,
                            "content-type": "application/x-www-form-urlencoded"
                        },
                    )

                    email = cast(dict[str, Any], email_response.json())[
                        'gmail']

                    if self.email_char_set.match(email):
                        if self.database is not None:
                            self.database.handle['email'].insert_one({
                                'email': email})
                        return email

                    else:
                        self.logger.debug(
                            'E-mail is in an invalid format. Generating another e-mail')
                        if self.database is not None:
                            self.database.handle['invalid_email'].insert_one({
                                'email': email})

            except (json.JSONDecodeError, KeyError):
                return self.get_random_database_email()

        def get_random_phone_number(self) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
            earlist_possible_date = datetime.utcnow() - timedelta(days=30)

            def fetch_phone_number_and_update_database(database: mongodb.Database) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
                while True:
                    random_phone_numbers = list(database.handle['randommer_io_phone_numbers'].aggregate([{'$match': {'$or': [{'last_used': None}, {'last_used': {'$lt': earlist_possible_date}}]}}, {'$sample': {'size': 1}}]))

                    if random_phone_numbers:
                        phone_number_doc = random_phone_numbers[0]
                        database.handle['randommer_io_phone_numbers'].update_one({'_id': phone_number_doc['_id']}, {'$set': {'last_used': datetime.utcnow()}})

                        return phone_number_doc['phone_number']

                    else:
                        bulk_phone_numbers_response = yield scrapy.FormRequest(
                            method='GET',
                            url='https://randommer.io/api/Phone/Generate',
                            headers={
                                "X-Api-Key": self.config.randommer_io.key,
                            },
                            formdata={
                                'CountryCode': 'US',
                                'Quantity': '1000',
                            }
                        )
                        phone_numbers = cast(list[str], bulk_phone_numbers_response.json())

                        database.handle['randommer_io_phone_numbers'].insert_many(({'phone_number': self.us_phone_number_pattern.sub(r'\1\2\3', phone_number), 'last_used': None} for phone_number in phone_numbers))

            return (yield from fetch_phone_number_and_update_database(self.database)) if self.database else '2052030652'

        def get_random_contact_info(self) -> Generator[scrapy.Request, scrapy.http.TextResponse, ContactInfo]:
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            email = yield from self.get_random_email()
            phone_number = yield from self.get_random_phone_number()

            return ContactInfo(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )

        def get_public_ip(self) -> Generator[scrapy.Request, scrapy.http.TextResponse, str]:
            public_ip_address_response = yield scrapy.FormRequest(
                method='GET',
                url='https://api.ipify.org/?',
                headers={
                    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
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
                formdata={
                    'format': 'json',
                },
            )

            return cast(dict[str, Any], public_ip_address_response.json())['ip']

        def get_random_scraper_api_proxy(self):
            num_proxies = 1_000_000_000_000  # A billion proxies is more than enough

            random_ip_id = random.randrange(num_proxies)

            username = f'scraperapi.country_code=us.premium=true.session_number={random_ip_id}.device_type=desktop'
            password = self.config.scraper_api.key
            host = 'proxy-server.scraperapi.com'
            port = 8001
            full_url = f'http://{username}:{password}@{host}:{port}'

            return Proxy(
                username=username,
                password=password,
                host=host,
                port=port,
                full_url=full_url,
            )

        def get_random_webshare_io_proxy(self):
            random_ip_id = random.randrange(
                self.config.webshare_io.num_proxies) + 1

            username = f'{self.config.webshare_io.username}-{random_ip_id}'
            password = self.config.webshare_io.password
            host = 'p.webshare.io'
            port = 12492
            full_url = f'http://{username}:{password}@{host}:{port}'

            return Proxy(
                username=username,
                password=password,
                host=host,
                port=port,
                full_url=full_url,
            )

        def __init__(self, batch_com: str, batch_id: str, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.socket_file = kwargs.get('socket_file', '')
            self.testing = kwargs.get('testing', 'false') == 'true'
            self.final_result = {}

            self.batch_com = int(batch_com)
            self.batch_id = int(batch_id)

            config_file = kwargs.get('config_file', 'config/scrabing_engine_config.toml')

            self.config = Config(config_file, self.source.lower())

            self.database = mongodb.Database(self.config.database) if kwargs.get('enable_database', 'true').lower() == 'true' else None

            # Create this after database to ensure it can send the logs before the database is closed
            self.log_handler = LogHandler(spider=self)

            self.vehicle_analyser = VehicleAnalyser()

            proxy_services: dict[str, Callable[[], Proxy]] = {
                'webshare_io': self.get_random_webshare_io_proxy,
                'scraper_api': self.get_random_scraper_api_proxy,
            }

            self.get_proxy = proxy_services[self.config.engine.proxy_service]

            self.collection_name = ('cars' if category == 'car_prices' else category) + ('_test' if self.testing else '')

            self.captcha_solver = CaptchaSolver()

        def vehicle_aspect_match_score(self, name1: str, name2: str):
            return self.vehicle_analyser.similarity_score(name1, name2, self.logger)

        def closed(self, _) -> None:
            pass

        def solving_recaptchav2_coroutine(self, website_url: str, website_key: str, proxy: str):
            return self.captcha_solver.solving_recaptchav2_coroutine(
                user_agent=self.settings['USER_AGENT'],
                website_url=website_url,
                website_key=website_key,
                capsolver_key=self.config.capsolver.key,
                proxy=proxy,
            )

        def solving_datadome_captcha_coroutine(
            self,
            website_url: str,
            captcha_url: str,
            proxy: str,
        ):
            return self.captcha_solver.solving_datadome_captcha_coroutine(
                user_agent=self.settings['USER_AGENT'],
                website_url=website_url,
                captcha_url=captcha_url,
                capsolver_key=self.config.capsolver.key,
                proxy=proxy,
            )

        def get_formatted_vin_details(self, details: dict[str, Any], autocheck_data: dict[str, Any]) -> VinDetails:
            year = int(details['year']['displayName'])
            make = details['make']['displayName']
            model = details['model']['displayName']
            trim = details['trim']['displayName']
            engine = details['engines'][0]['displayName']
            transmission = details['transmissions'][0]['displayName']
            drivetrain = details['drivetrains'][0]['displayName']
            # colour = details['colors'][0]['displayName']
            colour = 'Black'

            return VinDetails(
                kbb_details=details | {'vehicle_name': ' '.join(
                    [make, model, trim, drivetrain, engine, transmission])},
                year=year,
                make=make,
                model=model,
                trim=trim,
                engine=engine,
                transmission=transmission,
                drivetrain=drivetrain,
                colour=colour,
                autocheck_data=autocheck_data,
            )

        def get_vin_details(self, vin: str, trim: str) -> Generator[scrapy.Request, scrapy.http.TextResponse, VinDetails]:
            kbb_vin_decoded_response = yield scrapy.FormRequest(
                method='GET',
                url=f'https://api.kbb.com/ico/v1/vehicles/vin/{vin}/',
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-GB,en;q=0.9",
                    "content-type": "text/json",
                    "origin": "https://www.kbb.com",
                    "questionconversion": "fury",
                    "referer": "https://www.kbb.com/",
                    # "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
                    # "sec-ch-ua-mobile": "?0",
                    # "sec-ch-ua-platform": "\"Linux\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    # "traceid": "9a7286fd-9764-431c-b5b0-4c16f6c6dcf0",
                    # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                },
                formdata={
                    "cadsBypass": "false",
                    "vinVerified": "true",
                    "fromAuction": "undefined",
                    "api_key": "kehj9w5vxkt4t8yugn5zkpey"
                },
            )

            kbb_vin_decoded: Any = kbb_vin_decoded_response.json()

            if kbb_vin_decoded['meta']['codes'][0] == 400021:
                raise VinNotFound()

            kbb_vin_data = kbb_vin_decoded['data']
            possible_vehicles = kbb_vin_data['possibilities']
            possible_vehicles_trim_dict = {
                vehicle['trim']['displayName']: vehicle for vehicle in possible_vehicles}
            details = possible_vehicles_trim_dict[
                trim] if trim in possible_vehicles_trim_dict else possible_vehicles[0]

            return self.get_formatted_vin_details(details=details, autocheck_data=kbb_vin_data.get('autoCheckData', {}))

        def get_vin_details_if_not_exist(self, result) -> Generator[scrapy.Request, scrapy.http.TextResponse, dict]:
            return asdict((yield from self.get_vin_details(vin=cast(str, result['vin_number']), trim=cast(str, result['trim'])))) if 'kbb_details' not in result else {}

        def complete_request(self, request: scrapy.Request, request_metadata: RequestMetadata) -> scrapy.Request:
            elapsed_time_in_seconds = (
                datetime.utcnow() - request_metadata.start_time).total_seconds()

            if elapsed_time_in_seconds >= self.config.engine.timeout_in_seconds:
                raise ScrapingTimeout(url=request.url)

            return request.replace(
                dont_filter=True,
                errback=self.parse_error_response,
                meta={
                    'download_timeout': self.config.engine.timeout_in_seconds - elapsed_time_in_seconds,
                    'cookiejar': request_metadata.num_attempts,
                    'proxy': request_metadata.proxy.full_url,
                } | request.meta,
            )

        def get_relevant_details(self, previous_result: Result) -> dict:
            return asdict(self.get_formatted_vin_details(details=previous_result['kbb_details'], autocheck_data=previous_result['autocheck_data'])) if 'kbb_details' in previous_result else {}

        def process_requests(self, result: Result) -> Generator[Any, Any, Any]:
            yield result

        def get_additional_result_details(self) -> Result:
            return Result()

        def request_generator(self) -> Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result]:
            def generator(result: Result) -> Generator[Union[scrapy.Request, Result], Optional[Union[scrapy.http.Response, dict, list, str]], Result]:

                result = result | {'public_ip_address': (yield from self.get_public_ip()) if self.config.engine.proxy_service != 'scraper_api' else None}
                yield result
                result = result | (asdict((yield from self.get_random_contact_info())) | (yield from self.get_vin_details_if_not_exist(result)) if category == 'car_prices' else {})
                yield result

                requests = self.process_requests(result=result)
                item = next(requests)

                while type(item) is not Result:
                    response = yield item

                    item = requests.send(response)

                return item

            result = Result()
            previous_attempts: list[Result] = []
            absolute_start_time = datetime.utcnow()
            num_attempts = 0
            items = None

            while True:
                try:
                    self.logger.debug('Starting new attempt')
                    num_attempts = num_attempts + 1
                    proxy = self.get_proxy()
                    current_start_time = datetime.utcnow()

                    if items is not None:
                        previous_attempts.append(result)
                        items.close()

                    result = {
                        'num_attempts': num_attempts,
                        'start_time': current_start_time,
                        'success': 'true',
                        'source': self.source,
                        'proxy_username': proxy.username,
                        'proxy_password': proxy.password,
                        'proxy_address': proxy.host,
                        'proxy_port': proxy.port,
                        'proxy': proxy.full_url,
                    } | (self.get_relevant_details(previous_attempts[-1]) if len(previous_attempts) > 0 else {}) | self.get_additional_result_details()

                    # Fill out result details first before possibly throwing errors.
                    if num_attempts > self.config.engine.max_attempts:
                        raise MaxAttemptsReached

                    items = generator(result)
                    current_item = next(items)

                    while True:
                        if issubclass(type(current_item), scrapy.Request):
                            response, response_type = yield self.complete_request(request=cast(scrapy.Request, current_item), request_metadata=RequestMetadata(start_time=absolute_start_time, num_attempts=num_attempts, proxy=proxy))
                            item = response.headers.getlist('Set-Cookie') if response_type == 'cookie' else cast(dict, cast(scrapy.http.TextResponse, response).json()) if response_type == 'json' else response

                            current_item = items.send(item)

                        elif issubclass(type(current_item), Result):
                            result = cast(Result, current_item)
                            current_item = next(items)

                        else:
                            raise TypeError

                # The scipt received a response it hasn't encountered before and doesn't know how to process it.
                except (KeyError, IndexError, TypeError, AttributeError, TypeError, json.decoder.JSONDecodeError, UnencounteredResponse) as exception:
                    self.logger.error(exception, exc_info=True)

                    result['success'] = 'No offer'

                except (InvalidContactInfo, ContactInfoInUse, ProxyBlocked, CaptchaFailure, AutoCheckFailed, TwistedDNSLookupError, TwistedTunnelError, GenericTwistedError) as exception:
                    self.logger.error(str(exception), exc_info=True)

                    result['success'] = 'No offer'

                except OfferAlreadyExists as exception:
                    self.logger.error(str(exception), exc_info=True)

                    result['success'] = 'Already an active offer'
                    break

                except (OfferUnderReview, UnknownDealer, AccountNeeded, VinNotFound) as exception:
                    self.logger.error(str(exception), exc_info=True)

                    result['success'] = 'No offer'
                    break

                except CantMakeOfferForVin as exception:
                    self.logger.error(str(exception), exc_info=True)

                    result['success'] = 'Needs to see vehicle' if exception.needs_to_see_vehicle else 'No offer'
                    break

                except (MaxAttemptsReached, ScrapingTimeout) as exception:
                    self.logger.error(str(exception), exc_info=True)

                    result['success'] = 'Timeout'
                    break

                except StopIteration as exception:
                    result = exception.value
                    break

            return result | {
                'previous_attempts': previous_attempts,
                'end_time': datetime.utcnow(),
            }

        def initial_request(self) -> Union[scrapy.Request, Result]:
            try:
                request_generator = self.request_generator()
                first_request = next(request_generator)

                return first_request.replace(
                    cb_kwargs={
                        'request_generator': request_generator,
                    } | first_request.cb_kwargs,
                )

            except StopIteration as exception:
                return exception.value

        def start_requests(self) -> Generator[Union[scrapy.Request, Result], None, None]:
            yield self.initial_request()

        def parse_response_data(
            self,
            response: scrapy.http.Response,
            request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result],
            response_type: str
        ) -> Union[scrapy.Request, Result]:
            try:
                new_request = request_generator.send((response, response_type))
                return new_request.replace(
                    cb_kwargs={
                        'request_generator': request_generator,
                    } | new_request.cb_kwargs,
                )

            except StopIteration as exception:
                return exception.value

        def parse(
            self,
            response: scrapy.http.Response,
            request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result],
        ) -> Generator[Union[scrapy.Request, Result], None, None]:
            yield self.parse_response_data(response=response, request_generator=request_generator, response_type='default')

        def parse_response(
            self,
            response: scrapy.http.Response,
            request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result],
        ) -> Generator[Union[scrapy.Request, Result], None, None]:
            yield self.parse_response_data(response=response, request_generator=request_generator, response_type='default')

        def parse_json_response(
            self,
            response: scrapy.http.Response,
            request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result],
        ) -> Generator[Union[scrapy.Request, Result], None, None]:
            yield self.parse_response_data(response=response, request_generator=request_generator, response_type='json')

        def parse_cookie_response(
            self,
            response: scrapy.http.Response,
            request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result],
        ) -> Generator[Union[scrapy.Request, Result], None, None]:
            yield self.parse_response_data(response=response, request_generator=request_generator, response_type='cookie')

        def parse_error_response(self, failure: Any) -> Generator[Union[scrapy.Request, Result], None, None]:
            try:
                request: scrapy.Request = failure.request
                request_generator: Generator[scrapy.Request, Tuple[scrapy.http.Response, str], Result] = request.cb_kwargs['request_generator']

                if failure.check(HttpError):
                    response: scrapy.http.Response = failure.value.response

                    yield self.parse_response_data(response=response, request_generator=request_generator, response_type='default')

                elif failure.check(TimeoutError, TCPTimedOutError):
                    new_request = request_generator.throw(ScrapingTimeout(request.url))
                    yield new_request.replace(
                        cb_kwargs={
                            'request_generator': request_generator,
                        } | new_request.cb_kwargs,
                    )

                elif failure.check(DNSLookupError):
                    new_request = request_generator.throw(TwistedDNSLookupError(url=request.url))
                    yield new_request.replace(
                        cb_kwargs={
                            'request_generator': request_generator,
                        } | new_request.cb_kwargs,
                    )

                elif failure.check(TunnelError):
                    new_request = request_generator.throw(TwistedTunnelError())
                    yield new_request.replace(
                        cb_kwargs={
                            'request_generator': request_generator,
                        } | new_request.cb_kwargs,
                    )

                else:
                    new_request = request_generator.throw(GenericTwistedError(failure=failure))
                    yield new_request.replace(
                        cb_kwargs={
                            'request_generator': request_generator,
                        } | new_request.cb_kwargs,
                    )

            except StopIteration as exception:
                yield exception.value

    return Spider
