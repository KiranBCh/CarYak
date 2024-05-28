import scrapy
import scrapy.http
from car_prices.exceptions import CantMakeOfferForVin
from car_prices.spiders.car_prices import car_prices_spider


class CarPricesPeddleSpider(car_prices_spider(source='Peddle')):
    def process_requests(self, result):
        token_response = yield scrapy.Request(
            method='POST',
            url='https://sell.peddle.com/api/anonymous-token',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
            },
            callback=self.parse_json_response,
        )

        token = token_response['access_token']
        token_type = token_response['token_type']

        vin_details_response = yield scrapy.Request(
            url=f'https://service.peddle.com/universal/v3/vins/{result["vin_number"]}',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': f'{token_type} {token}',
            },
        )

        if vin_details_response.status >= 400:
            raise CantMakeOfferForVin(needs_to_see_vehicle=False)
        else:
            vin_details_response = vin_details_response.json()

        year_id = vin_details_response['year']['id'] if 'year' in vin_details_response else ''
        make_id = vin_details_response['make']['id'] if 'make' in vin_details_response else ''

        model_id = vin_details_response['model']['id'] if 'model' in vin_details_response else ''
        model_info = vin_details_response['model'] if 'model' in vin_details_response else {
        }

        body_type_id = model_info['body_type']['id'] if 'body_type' in model_info else ''
        cab_type_id = model_info['cab_type']['id'] if 'cab_type' in model_info else ''
        door_count = model_info['door_count'] if 'door_count' in model_info else ''

        trim_id = vin_details_response['trim']['id'] if 'trim' in vin_details_response else ''
        trim_info = vin_details_response['trim'] if 'trim' in vin_details_response else {
        }

        body_style_id = trim_info['body_style']['id'] if 'body_style' in trim_info else ''
        fuel_type_id = trim_info['fuel_type']['id'] if 'fuel_type' in trim_info else ''

        condition_data = {
            'mileage': result['mileage'],
            'drivetrain_condition': 'drives',
            'key_and_keyfob_available': 'yes',
            'all_tires_inflated': 'yes',
            'flat_tires_location': {
                'driver_side_view': {
                    'front': False,
                    'rear': False,
                },
                'passenger_side_view': {
                    'front': False,
                    'rear': False,
                },
            },
            'wheels_removed': 'no',
            'wheels_removed_location': {
                'driver_side_view': {
                    'front': False,
                    'rear': False,
                },
                'passenger_side_view': {
                    'front': False,
                    'rear': False,
                },
            },
            'body_panels_intact': 'yes',
            'body_panels_damage_location': {
                'driver_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'passenger_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'front_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'rear_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'top_view': {
                    'driver_side_front': False,
                    'passenger_side_front': False,
                    'driver_side_front_roof': False,
                    'passenger_side_front_roof': False,
                    'driver_side_rear_roof': False,
                    'passenger_side_rear_roof': False,
                    'driver_side_rear': False,
                    'passenger_side_rear': False,
                },
            },
            'body_damage_free': 'yes',
            'body_damage_location': {
                'driver_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'passenger_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'front_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'rear_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'top_view': {
                    'driver_side_front': False,
                    'passenger_side_front': False,
                    'driver_side_front_roof': False,
                    'passenger_side_front_roof': False,
                    'driver_side_rear_roof': False,
                    'passenger_side_rear_roof': False,
                    'driver_side_rear': False,
                    'passenger_side_rear': False,
                },
            },
            'mirrors_lights_glass_intact': 'yes',
            'mirrors_lights_glass_damage_location': {
                'driver_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'passenger_side_view': {
                    'front_top': False,
                    'front_bottom': False,
                    'front_door_top': False,
                    'front_door_bottom': False,
                    'rear_door_top': False,
                    'rear_door_bottom': False,
                    'rear_top': False,
                    'rear_bottom': False,
                },
                'front_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'rear_view': {
                    'driver_side_top': False,
                    'driver_side_bottom': False,
                    'passenger_side_top': False,
                    'passenger_side_bottom': False,
                },
                'top_view': {
                    'driver_side_front': False,
                    'passenger_side_front': False,
                    'driver_side_front_roof': False,
                    'passenger_side_front_roof': False,
                    'driver_side_rear_roof': False,
                    'passenger_side_rear_roof': False,
                    'driver_side_rear': False,
                    'passenger_side_rear': False,
                },
            },
            'interior_intact': 'yes',
            'flood_fire_damage_free': 'yes',
            'engine_transmission_condition': 'intact',
            'catalytic_converter_intact': 'yes',
        }

        ownership_data = {
            'type': 'owned',
            'title_type': 'clean',
        }

        result['Ownership'] = ownership_data['type'].title()
        result['Title'] = ownership_data['title_type'].title()

        result['Drivetrain Condition'] = condition_data['drivetrain_condition'].title()
        result['Key and keyfob available'] = condition_data['key_and_keyfob_available'].title()
        result['All tires inflated'] = condition_data['all_tires_inflated'].title()
        result['Front driver side view tire not inflated'] = condition_data['flat_tires_location']['driver_side_view']['front']
        result['Front driver side view tire not inflated'] = condition_data['flat_tires_location']['driver_side_view']['rear']
        result['Front Passenger side view tire not inflated'] = condition_data['flat_tires_location']['passenger_side_view']['front']
        result['Rear Passenger side view tire not inflated'] = condition_data['flat_tires_location']['passenger_side_view']['rear']
        result['Wheels removed'] = condition_data['wheels_removed'].title()
        result['wheel removed'] = condition_data['wheels_removed_location']['driver_side_view']['front']
        result['wheel removed'] = condition_data['wheels_removed_location']['driver_side_view']['rear']
        result['wheel removed'] = condition_data['wheels_removed_location']['passenger_side_view']['front']
        result['wheel removed'] = condition_data['wheels_removed_location']['passenger_side_view']['rear']
        result['Body panels intact'] = condition_data['body_panels_intact'].title()
        result['Front top driver side view body panel damaged'] = condition_data['body_panels_damage_location']['driver_side_view']['front_top']
        result['Front bottom driver side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['driver_side_view']['front_bottom']
        result['Front door top driver side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['driver_side_view']['front_door_top']
        result['Front door bottom driver side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['driver_side_view']['front_door_bottom']
        result['Rear door top driver side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['driver_side_view']['rear_door_top']
        result['Rear door bottom driver side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['driver_side_view']['rear_door_bottom']
        result['Rear top driver side view body panel damaged'] = condition_data['body_panels_damage_location']['driver_side_view']['rear_top']
        result['Rear bottom driver side view body panel damaged'] = condition_data['body_panels_damage_location']['driver_side_view']['rear_bottom']
        result['Front top passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['front_top']
        result['Front bottom passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['front_bottom']
        result['Front door top passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['front_door_top']
        result['Front door bottom passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['front_door_bottom']
        result['Rear door top passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['rear_door_top']
        result['Rear door bottom passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['rear_door_bottom']
        result['Rear top passenger side view body panel damaged'] = condition_data['body_panels_damage_location']['passenger_side_view']['rear_top']
        result['Rear bottom passenger side view body panel damaged'] = condition_data[
            'body_panels_damage_location']['passenger_side_view']['rear_bottom']
        result['Driver side top front view body panel damaged'] = condition_data['body_panels_damage_location']['front_view']['driver_side_top']
        result['Driver side bottom front view body panel damaged'] = condition_data[
            'body_panels_damage_location']['front_view']['driver_side_bottom']
        result['Passenger side top front view body panel damaged'] = condition_data[
            'body_panels_damage_location']['front_view']['passenger_side_top']
        result['Passenger side bottom front view body panel damaged'] = condition_data[
            'body_panels_damage_location']['front_view']['passenger_side_bottom']
        result['Driver side top rear view body panel damaged'] = condition_data['body_panels_damage_location']['rear_view']['driver_side_top']
        result['Driver side bottom rear view body panel damaged'] = condition_data['body_panels_damage_location']['rear_view']['driver_side_bottom']
        result['Passenger side top rear view body panel damaged'] = condition_data['body_panels_damage_location']['rear_view']['passenger_side_top']
        result['Passenger side bottom rear view body panel damaged'] = condition_data[
            'body_panels_damage_location']['rear_view']['passenger_side_bottom']
        result['Driver side front top view body panel damaged'] = condition_data['body_panels_damage_location']['top_view']['driver_side_front']
        result['Passenger side front top view body panel damaged'] = condition_data[
            'body_panels_damage_location']['top_view']['passenger_side_front']
        result['Driver side front roof top view body panel damaged'] = condition_data[
            'body_panels_damage_location']['top_view']['driver_side_front_roof']
        result['Passenger side front roof top view body panel damaged'] = condition_data[
            'body_panels_damage_location']['top_view']['passenger_side_front_roof']
        result['Driver side rear roof top view body panel damaged'] = condition_data[
            'body_panels_damage_location']['top_view']['driver_side_rear_roof']
        result['Passenger side rear roof top view body panel damaged'] = condition_data[
            'body_panels_damage_location']['top_view']['passenger_side_rear_roof']
        result['Driver side rear top view body panel damaged'] = condition_data['body_panels_damage_location']['top_view']['driver_side_rear']
        result['Passenger side rear top view body panel damaged'] = condition_data['body_panels_damage_location']['top_view']['passenger_side_rear']
        result['Body damage free'] = condition_data['body_damage_free'].title()
        result['Front top driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['front_top']
        result['Front bottom driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['front_bottom']
        result['Front door top driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['front_door_top']
        result['Front door bottom driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['front_door_bottom']
        result['Rear door top driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['rear_door_top']
        result['Rear door bottom driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['rear_door_bottom']
        result['Rear top driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['rear_top']
        result['Rear bottom driver side view body damaged'] = condition_data['body_damage_location']['driver_side_view']['rear_bottom']
        result['Front top passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['front_top']
        result['Front bottom passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['front_bottom']
        result['Front door top passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['front_door_top']
        result['Front door bottom passenger side view body damaged'] = condition_data[
            'body_damage_location']['passenger_side_view']['front_door_bottom']
        result['Rear door top passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['rear_door_top']
        result['Rear door bottom passenger side view body damaged'] = condition_data[
            'body_damage_location']['passenger_side_view']['rear_door_bottom']
        result['Rear top passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['rear_top']
        result['Rear bottom passenger side view body damaged'] = condition_data['body_damage_location']['passenger_side_view']['rear_bottom']
        result['Driver side top front view body damaged'] = condition_data['body_damage_location']['front_view']['driver_side_top']
        result['Driver side bottom front view body damaged'] = condition_data['body_damage_location']['front_view']['driver_side_bottom']
        result['Passenger side top front view body damaged'] = condition_data['body_damage_location']['front_view']['passenger_side_top']
        result['Passenger side bottom front view body damaged'] = condition_data['body_damage_location']['front_view']['passenger_side_bottom']
        result['Driver side top rear view body damaged'] = condition_data['body_damage_location']['rear_view']['driver_side_top']
        result['Driver side bottom rear view body damaged'] = condition_data['body_damage_location']['rear_view']['driver_side_bottom']
        result['Passenger side top rear view body damaged'] = condition_data['body_damage_location']['rear_view']['passenger_side_top']
        result['Passenger side bottom rear view body damaged'] = condition_data['body_damage_location']['rear_view']['passenger_side_bottom']
        result['Driver side front top view body damaged'] = condition_data['body_damage_location']['top_view']['driver_side_front']
        result['Passenger side front top view body damaged'] = condition_data['body_damage_location']['top_view']['passenger_side_front']
        result['Driver side front roof top view body damaged'] = condition_data['body_damage_location']['top_view']['driver_side_front_roof']
        result['Passenger side front roof top view body damaged'] = condition_data['body_damage_location']['top_view']['passenger_side_front_roof']
        result['Driver side rear roof top view body damaged'] = condition_data['body_damage_location']['top_view']['driver_side_rear_roof']
        result['Passenger side rear roof top view body damaged'] = condition_data['body_damage_location']['top_view']['passenger_side_rear_roof']
        result['Driver side rear top view body damaged'] = condition_data['body_damage_location']['top_view']['driver_side_rear']
        result['Passenger side rear top view body damaged'] = condition_data['body_damage_location']['top_view']['passenger_side_rear']
        result['Mirrors lights glass intact'] = condition_data['mirrors_lights_glass_intact'].title()
        result['Front top driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['front_top']
        result['Front bottom driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['front_bottom']
        result['Front door top driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['front_door_top']
        result['Front door bottom driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['front_door_bottom']
        result['Rear door top driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['rear_door_top']
        result['Rear door bottom driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['rear_door_bottom']
        result['Rear top driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['rear_top']
        result['Rear bottom driver side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['driver_side_view']['rear_bottom']
        result['Front top passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['front_top']
        result['Front bottom passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['front_bottom']
        result['Front door top passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['front_door_top']
        result['Front door bottom passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['front_door_bottom']
        result['Rear door top passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['rear_door_top']
        result['Rear door bottom passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['rear_door_bottom']
        result['Rear top passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['rear_top']
        result['Rear bottom passenger side view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['passenger_side_view']['rear_bottom']
        result['Driver side top front view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['front_view']['driver_side_top']
        result['Driver side bottom front view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['front_view']['driver_side_bottom']
        result['Passenger side top front view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['front_view']['passenger_side_top']
        result['Passenger side bottom front view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['front_view']['passenger_side_bottom']
        result['Driver side top rear view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['rear_view']['driver_side_top']
        result['Driver side bottom rear view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['rear_view']['driver_side_bottom']
        result['Passenger side top rear view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['rear_view']['passenger_side_top']
        result['Passenger side bottom rear view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['rear_view']['passenger_side_bottom']
        result['Driver side front top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['driver_side_front']
        result['Passenger side front top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['passenger_side_front']
        result['Driver side front roof top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['driver_side_front_roof']
        result['Passenger side front roof top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['passenger_side_front_roof']
        result['Driver side rear roof top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['driver_side_rear_roof']
        result['Passenger side rear roof top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['passenger_side_rear_roof']
        result['Driver side rear top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['driver_side_rear']
        result['Passenger side rear top view mirrors lights glass damaged'] = condition_data[
            'mirrors_lights_glass_damage_location']['top_view']['passenger_side_rear']
        result['Interior intact'] = condition_data['interior_intact']
        result['Flood fire damage free'] = condition_data['flood_fire_damage_free']
        result['Engine transmission condition'] = condition_data['engine_transmission_condition']

        offer_response = yield scrapy.http.JsonRequest(
            url=f'https://service.peddle.com/seller/v4/instant-offers',
            headers={
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': f'{token_type} {token}',
                'content-type': 'application/json',
            },
            data={
                'vehicle': {
                    'year_id': year_id,
                    'make_id': make_id,
                    'model_id': model_id,
                    'body_type_id': body_type_id,
                    'cab_type_id': cab_type_id,
                    'door_count': door_count,
                    'trim_id': trim_id,
                    'body_style_id': body_style_id,
                    'fuel_type_id': fuel_type_id,
                    'vin': result['vin_number'],
                    'usage': 'unknown',
                    'location': {
                        'zip_code': result['zip_code'],
                    },
                    'ownership': ownership_data,
                    'condition': condition_data,
                },
                'publisher': {},
            },
            callback=self.parse_json_response,
        )

        price = float(offer_response['presented_offer_amount'])

        result['price'] = price

        yield result
