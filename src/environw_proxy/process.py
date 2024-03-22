# -*- coding: utf-8 -*-
"""Module containing functions for processing weather records."""
import json
import os
import urllib.parse
from dataclasses import asdict
from datetime import datetime
from enum import Enum

import requests  # trunk-ignore(pyright/reportMissingModuleSource)
from aws_lambda_powertools import Logger, Tracer  # trunk-ignore(pyright/reportMissingImports)

from environw_proxy.objects import (  # trunk-ignore(pyright/reportMissingImports)
    EnvironWRecord,
    Station,
    WindyObservationRecord,
)

tracer: Tracer = Tracer(service="weather-proxy")
logger: Logger = Logger(service="weather-proxy", utc=True, child=True)


def get_station_value(station_name: str) -> int:
    """Get the value of a station based on its name.
    
    Args:
        station_name (str): The name of the station.
    
    Returns:
        int: The value of the station.
    """
    # Normalize the input to match the enumeration naming convention
    normalized_input = ''.join(filter(str.isalnum, station_name)).upper()
    
    # Attempt to match the normalized input with an enum member
    for station in Station:
        if station.name == normalized_input:
            return station.value

    # Default return value if no match is found
    return 0


def mps_to_mph(speed_mps: float) -> float:
    """Convert speed from m/s to mph.

    Args:
        speed_mps (float): The speed in meters per second.

    Returns:
        float: The speed in miles per hour.
    """
    return speed_mps * 2.23694


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert temperature from Fahrenheit to Celsius.

    Args:
        fahrenheit (float): Temperature in Fahrenheit.

    Returns:
        float: Temperature in Celsius.
    """
    return (fahrenheit - 32) * 5 / 9



def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert temperature from Celsius to Fahrenheit.

    Args:
        celsius (float): Temperature in Celsius.

    Returns:
        float: Temperature in Fahrenheit.
    """
    return (celsius * 9 / 5) + 32

def mm_to_inches(length_mm: float) -> float:
    """Convert length from millimeters to inches.

    Args:
        length_mm (float): mm length.

    Returns:
        float: inches length.
    """
    return length_mm * 0.0393701


def convert_date_time(date_time: str) -> str:
    """Convert date and time to a format that can be used in the API.

    Args:
        date_time (str): The date and time.

    Returns:
        str: The date and time in the correct format, urlescaped.
    """
    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    formatted_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    return urllib.parse.quote_plus(formatted_str)

def get_source_object(event: EnvironWRecord) -> list[WindyObservationRecord]:
    """Get the source object from the EnvironWRecord event.

    Args:
        event (EnvironWRecord): The EnvironWRecord event.

    Returns:
        list[WindyObservationRecord]: The list of WindyObservationRecord objects.
    """
    weather_records: list[WindyObservationRecord] = []

    logger.info(f'Weather Record: {event}')
    station = get_station_value(event['nickname'])
    weather_records.append(WindyObservationRecord(
        temp=event['readings']['temperature'],
        wind=event['readings']['wind_speed'],
        windir=event['readings']['wind_direction'],
        gust=0,
        humidity=event['readings']['humidity'],
        dewpoint=0,
        pressure=event['readings']['pressure'],
        precip=event['readings']['rain'],
        uv=event['readings']['light'],
        station=station,
        time=event['timestamp']
    ))

    return weather_records


def complex_handler(obj):
    """Custom JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, Enum):
        return obj.value  # Or obj.name if you prefer to serialize the enum name
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    if isinstance(obj, set):
        return list(obj)  # Convert sets to lists
    msg_handler = f"Object of type {obj.__class__.__name__} is not JSON serializable"
    raise TypeError(msg_handler)


def post_records_windy(json_payload: dict) -> bool:
    """Post the weather records to the Windy API.

    Args:
        json_payload (dict): The list of WindyObservationRecord objects.

    Returns:
        bool: True if the records are successfully posted.
    """
    logger.debug(f"Posting {len(json_payload)} weather records")
    success_status_code = 200

    api_key = os.environ.get("WINDY_API_KEY", None)
    if api_key is None:
        logger.error("WINDY_API_KEY environment variable not set")
        return False
    endpoint_url = f"https://stations.windy.com/pws/update/{api_key}"

    headers = {
    'Content-Type': 'application/json'
    }

    try:
        logger.info(f"Posting Observation record: {json_payload}")
        # Make the POST request with a timeout of 5 seconds
        response = requests.post(endpoint_url, json=json_payload, headers=headers, timeout=5)
        # Check the response
        if response.status_code == success_status_code:
            print("Data successfully posted to Windy.com")
        else:
            print("Failed to post data:", response.text)
    except requests.exceptions.RequestException as err:
        logger.error(f"Error submitting weather record: {str(err)}")
        return False
    return True


def create_observation_record(event: EnvironWRecord) -> WindyObservationRecord:
    """Create a WindyObservationRecord object from an EnvironWRecord event.

    Args:
        event (EnvironWRecord): The EnvironWRecord event.

    Returns:
        WindyObservationRecord: The WindyObservationRecord object.
    """
    return WindyObservationRecord(
        temp=event['readings']['temperature'],
        wind=event['readings']['wind_speed'],
        windir=event['readings']['wind_direction'],
        humidity=event['readings']['humidity'],
        pressure=event['readings']['pressure'],
        precip=event['readings']['rain'],
        station=get_station_value(event['nickname']),
        time=event['timestamp']
    )


def post_records_wunderground(event: EnvironWRecord) -> bool:
    """Post the weather records to the Wunderground API.

    Args:
        event (EnvironWRecord): The EnvironWRecord event.

    Returns:
        bool: True if the records are successfully posted.
    """
    url_wunderground = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
    station_id = os.environ.get(f"WUNDERGROUND_STATION_ID_{get_station_value(event['nickname'])}", None)
    station_key = os.environ.get(f"WUNDERGROUND_STATION_KEY_{get_station_value(event['nickname'])}", None)
    if station_id is None or station_key is None:
        logger.error("WUNDERGROUND_STATION_ID or WUNDERGROUND_STATION_KEY environment variables not set")
        return False
    try:
        parameters = f"ID={station_id}&PASSWORD={station_key}&dateutc={convert_date_time(event['timestamp'])}&winddir={event['readings']['wind_direction']}&windspeedmph={mps_to_mph(event['readings']['wind_speed'])}&tempf={celsius_to_fahrenheit(event['readings']['temperature'])}&rainin={mm_to_inches(event['readings']['rain'])}&humidity={event['readings']['humidity']}&baromin={event['readings']['pressure']}&action=updateraw"
        logger.debug(f"Subbmitting to Wunderground: {parameters}")
        result = requests.get(f"{url_wunderground}?{parameters}", timeout=5)
        logger.debug(f"Successfully posted to Wunderground, {result.text}, {result.status_code}")
        return True
    except requests.exceptions.RequestException as err:
        logger.error(f"Error submitting weather record: {str(err)}")
        return False


def process_windy_records(event: EnvironWRecord) -> bool:
    """Process the weather records.

    Args:
        event (EnvironWRecord): The EnvironWRecord event.

    Returns:
        bool: True if the records are successfully processed.
    """
    weather_records: list[WindyObservationRecord] = get_source_object(event=event)
    logger.debug(f"Total records to process: {len(weather_records)}")
    observations: list = []
    for record in weather_records:
        observations.append(json.dumps(asdict(record), default=complex_handler))
    json_payload = {
        'observations': observations
    }

    return post_records_windy(json_payload=json_payload)
