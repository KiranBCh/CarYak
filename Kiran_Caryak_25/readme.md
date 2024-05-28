# Scrabbing Engine
An engine designed to scrape the web for car appraisal information.

## Dependencies
This project requires:
- Python >= 3.10
- PDM >= 2.4

## Setup
To install the software, first run `pdm install` to install the necessary Python libraries.

## Basic usage
To use the engine, run:
```
pdm run scrapy crawl car_prices -a config_file=<file location> -a enable_database=<true|false> -a batch_id=<batch id> -a first_name=<first name> -a last_name=<last name> -a email=<e-mail> -a phone_number=<phone number> -a vin=<vin number> -a trim=<KBB trim name> -a zip_code=<zip code> -a mileage=<mileage> -a batch_com=<batch com> -a condition=<bad|moderate|good|excellent>
```

Here is an example of a config file:
```
[engine]
timeout_in_seconds = <maximum time in seconds for the scraping to take before it gives up>
max_attempts = <maximum number of attempts of getting the offer>
proxy_service = <Name of the proxy service to use. e.g. webshare_io, scraper_api>
[database]
username = <database username>
password = <database password>
ca_file = <database certificate authority file>
host = <database host url>
port = <database port>
name = <database name>
[scraper_api]
key = <ScraperAPI API key>
[webshare_io]
key=<WebShare.io API key>
mode = <WebShare.io connection mode>
[capsolver]
key=<CapSolver API key>
[site_override.<Name of site e.g. kbb_ico>]
engine.timeout_in_seconds = 300
engine.proxy_service = "scraper_api"
[site_override.<Some other site>]
# Other site specific setting you want
```

Once the engine finishes, all scraped data will automatically be sent to the MongoDB database specified in the config file. You may run this command as many times as you want to scrape different data.
