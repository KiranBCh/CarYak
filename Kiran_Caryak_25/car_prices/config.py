from typing import Any
import toml


def load_config(config_file: str):
    with open(config_file, 'r') as file:
        return toml.loads(file.read())


class MergedConfig:
    def __init__(self, global_config: dict, site_config: dict):
        self.global_config = global_config
        self.site_config = site_config

    def get_attribute(self, attribute_name: str, default_value: Any = None):
        return self.site_config.get(attribute_name, self.global_config.get(attribute_name, default_value))

    def load_subconfig(self, subconfig_name: str):
        return MergedConfig(global_config=self.global_config.get(subconfig_name, {}), site_config=self.site_config.get(subconfig_name, {}))


class Engine:
    def __init__(self, config: MergedConfig):
        self.timeout_in_seconds: int = config.get_attribute(
            'timeout_in_seconds', 30)
        self.max_attempts: int = config.get_attribute('max_attempts', 5)
        self.proxy_service: str = config.get_attribute(
            'proxy_service', 'webshare_io')


class RapidApi:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')


class RandommerIo:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')


class DisposableGmail:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')


class Database:
    def __init__(self, config: MergedConfig):
        self.username: str = config.get_attribute('username', 'admin')
        self.password: str = config.get_attribute('password', 'password')
        self.ca_file: str = config.get_attribute('ca_file', 'ca_file.pem')
        self.host: str = config.get_attribute('host', 'localhost')
        self.port: int = config.get_attribute('port', 27017)
        self.name: str = config.get_attribute('name', 'Scrabing_engine')


class ScraperApi:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')


class WebshareIo:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')
        self.username: str = config.get_attribute('username', 'username')
        self.password: str = config.get_attribute('password', 'password')
        self.num_proxies: int = config.get_attribute('num_proxies', 100)


class CapSolver:
    def __init__(self, config: MergedConfig):
        self.key: str = config.get_attribute('key', 'this_is_not_a_real_key')


class Config:
    def __init__(self, config_file: str, site_name: str):
        config = load_config(config_file)
        parsed_config = MergedConfig(
            global_config=config, site_config=config.get('site_override', {}).get(site_name, {}))
        self.engine = Engine(parsed_config.load_subconfig('engine'))
        self.rapid_api = RapidApi(parsed_config.load_subconfig('rapid_api'))
        self.randommer_io = RapidApi(parsed_config.load_subconfig('randommer_io'))
        self.disposable_gmail = DisposableGmail(
            parsed_config.load_subconfig('disposable_gmail'))
        self.database = Database(parsed_config.load_subconfig('database'))
        self.scraper_api = ScraperApi(
            parsed_config.load_subconfig('scraper_api'))
        self.webshare_io = WebshareIo(
            parsed_config.load_subconfig('webshare_io'))
        self.capsolver = CapSolver(parsed_config.load_subconfig('capsolver'))
