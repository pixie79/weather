# -*- coding: utf-8 -*-
"""Module containing functions for processing weather records."""
import json
import os
from dataclasses import asdict
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


def post_records(weather_records: list[WindyObservationRecord]) -> bool:
    """Post the weather records to the Windy API.

    Args:
        weather_records (list[WindyObservationRecord]): The list of WindyObservationRecord objects.

    Returns:
        bool: True if the records are successfully posted.
    """
    logger.debug(f"Posting {len(weather_records)} weather records")
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
        for record in weather_records:
            json_data = json.dumps(asdict(record), default=complex_handler)
            # Make the POST request with a timeout of 5 seconds
            response = requests.post(endpoint_url, json=json_data, headers=headers, timeout=5)
            # Check the response
            if response.status_code == success_status_code:
                print("Data successfully posted to Windy.com")
            else:
                print("Failed to post data:", response.text)
    except requests.exceptions.RequestException as err:
        logger.error(f"Error submitting weather record: {str(err)}")
        return False
    return True


def process_records(event: EnvironWRecord) -> bool:
    """Process the weather records.

    Args:
        event (EnvironWRecord): The EnvironWRecord event.

    Returns:
        bool: True if the records are successfully processed.
    """
    weather_records: list[WindyObservationRecord] = get_source_object(event=event)
    logger.debug(f"Total records to process: {len(weather_records)}")
    logger.debug(f"WeatherRecord: {weather_records}")
    return post_records(weather_records=weather_records)
