# -*- coding: utf-8 -*-
"""Module containing classes for weather station observation records and Windy station records."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union


@dataclass
class EnvironWRecordReadings:
    """Class representing the readings for an EnvironW Readings record."""
    pressure: float
    wind_speed: float
    rain: float
    wind_direction: int
    humidity: float
    temperature: float
    light: float


@dataclass
class EnvironWRecord:
    """Class representing the readings for an EnvironW record."""
    readings: EnvironWRecordReadings
    nickname: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))


@dataclass
class WindyObservationRecord: # trunk-ignore(pylint/R0902)
    """Class representing an observation record for a weather station.

    Attributes:
        station (int): A unique 32-bit integer ID for the station. Can also be set using `si` or `stationId`.
        time (str): The primary representation of observation time in ISO 8601 UTC format.
        temp (float): Air temperature in °C. Can also be set using `tempf` (in Fahrenheit).
        wind (float): Wind speed in m/s. Can also be set using `windspeedmph` (in mph).
        windir (int): Instantaneous wind direction in degrees.
        gust (float): Current wind gust in m/s. Can also be set using `windgustmph` (in mph).
        humidity (float): Current humidity in %. Can also be set using `rh`.
        dewpoint (float): Dewpoint in °C.
        pressure (float): Atmospheric pressure in Pa. Can also be set using `mbar` or `baromin`.
        precip (float): Precipitation over the past hour in mm. Can also be set using `rainin` (in inches).
        uv (float): UV index.

    Note:
        Alternative names and units for several fields are accepted during initialization.
        Conversions are applied for temperature, wind speed, and precipitation from imperial to metric units.
    """
    temp: Optional[Union[int, float]]
    wind: Optional[Union[int, float]]
    windir: Optional[int]
    gust: Optional[Union[int, float]]
    humidity: Optional[float]
    dewpoint: Optional[float]
    pressure: Optional[float]
    precip: Optional[Union[int, float]]
    uv: Optional[Union[int,float]]
    # Alternative names and units
    si: Union[int, None] = field(default=None, repr=False)
    stationId: Union[int, None] = field(default=None, repr=False)  # trunk-ignore(pylint/C0103)
    dateutc: Union[str, None] = field(default=None, repr=False)
    ts: Union[str, None] = field(default=None, repr=False)
    tempf: Union[int, float, None] = field(default=None, repr=False)
    windspeedmph: Union[int, float, None] = field(default=None, repr=False)
    windgustmph: Union[int, float, None] = field(default=None, repr=False)
    rh: Union[int, None] = field(default=None, repr=False)
    mbar: Union[int, None] = field(default=None, repr=False)
    baromin: Union[int, float, None] = field(default=None, repr=False)
    rainin: Union[int, float, None] = field(default=None, repr=False)
    station: int = 0
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + 'Z')

    def __post_init__(self):
        """Initialize the object after it has been created. Allows handling of alternative names and units."""
        self.station = self.si if self.si is not None else self.station
        self.station = self.stationId if self.stationId is not None else self.station
        if self.ts is not None:
            # Assuming ts is given in seconds. Convert to datetime object then to ISO format.
            self.time = datetime.fromtimestamp(int(self.ts), tz=timezone.utc).isoformat() + 'Z'
        elif self.dateutc is not None:
            dt_obj = datetime.strptime(self.dateutc, "%Y-%m-%d %H:%M:%S")
            self.time = dt_obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if self.tempf is not None:
            self.temp = (self.tempf - 32) * 5 / 9  # Convert Fahrenheit to Celsius
        if self.windspeedmph is not None:
            self.wind = self.windspeedmph * 0.44704  # Convert mph to m/s
        if self.windgustmph is not None:
            self.gust = self.windgustmph * 0.44704  # Convert mph to m/s
        self.humidity = self.rh if self.rh is not None else self.humidity
        self.pressure = self.mbar if self.mbar is not None else self.pressure
        self.pressure = self.baromin * 3386.39 if self.baromin is not None else self.pressure  # Convert inches Hg to Pa
        if self.rainin is not None:
            self.precip = self.rainin * 25.4  # Convert inches to mm


class WindyShareOption(Enum):
    """Enum representing the share option status of a Windy station.

    Attributes:
        OPEN (str): The station's data is open to the public.
        ONLY (str): The station's data is only available within the Windy community.
        PRIVATE (str): The station's data is private and not shared.
    """
    OPEN = "Open"
    ONLY = "Only Windy"
    PRIVATE = "Private"


class Station(Enum):
    """An enumeration representing weather stations."""
    OLLIVERHOME = 0
    LIZARDHUBS = 1


@dataclass
class WindyStationRecord: # trunk-ignore(pylint/R0902)
    """A record representing a weather station in the Windy ecosystem.

    Attributes:
        station (int): A unique 32-bit integer ID for the station. Can also be set using `si` or `stationId`.
        shareOption (WindyShareOption): The sharing option of the station's data, defaulting to OPEN.
        lat (float): The latitude of the station in degrees. Valid range is -90 to 90.
        lon (float): The longitude of the station in degrees. Valid range is -180 to 180.
        elevation (int): The elevation of the station in meters above sea level. Can also be set using `elev`, `elev_m`, or `altitude`.
        tempheight (int): The height of the temperature sensors above the surface in meters. Can also be set using `agl_temp`.
        windheight (int): The height of the wind sensors above the surface in meters. Can also be set using `agl_wind`.

    Note:
        Latitude (`lat`) and Longitude (`lon`) values are enforced to be within their correct geographical ranges.
        Alternative names for `station` and `elevation` are supported through the class initialization process.
    """
    _lat: float = field(init=False)
    _lon: float = field(init=False)
    elevation: int
    tempheight: int
    windheight: int
    station: Optional[int] = None
    si: Union[int, None] = field(default=None, repr=False)
    stationId: Union[int, None] = field(default=None, repr=False)  # trunk-ignore(pylint/C0103)
    elev: Union[int, None] = field(default=None, repr=False)
    elev_m: Union[int, None] = field(default=None, repr=False)
    altitude: Union[int, None] = field(default=None, repr=False)
    agl_temp: Union[int, None] = field(default=None, repr=False)
    agl_wind: Union[int, None] = field(default=None, repr=False)
    shareOption: WindyShareOption = field(default_factory=lambda: WindyShareOption.OPEN)  # trunk-ignore(pylint/C0103)

    def __post_init__(self):
        """Initialize the object after it has been created."""
        if self.station is not None:
            self.station = self.station
        elif self.si is not None:
            self.station = self.si
        elif self.stationId is not None:
            self.station = self.stationId
        else:
            self.station = 0
        
        self.elevation = self.elev if self.elev is not None else self.elevation
        self.elevation = self.elev_m if self.elev_m is not None else self.elevation
        self.elevation = self.altitude if self.altitude is not None else self.elevation

        self.tempheight = self.agl_temp if self.agl_temp is not None else self.tempheight
        self.windheight = self.agl_wind if self.agl_wind is not None else self.windheight

    @property
    def lat(self):
        """Property for the latitude value."""
        return self._lat

    LATITUDE_RANGE = 90

    @lat.setter
    def lat(self, value):
        """Set the latitude value.
        
        Args:
            value (float): The latitude value to be set.
        
        Raises:
            ValueError: If the latitude value is not within the valid range.
        """
        if not -self.LATITUDE_RANGE <= value <= self.LATITUDE_RANGE:
            msglat = "Latitude must be between -90 and 90 degrees."
            raise ValueError(msglat)
        self._lat = value

    @property
    def lon(self):
        """Property for the longitude value."""
        return self._lon

    MAX_LONGITUDE = 180

    @lon.setter
    def lon(self, value):
        """Set the longitude value.

        Args:
            value (float): The longitude value to be set.

        Raises:
            ValueError: If the longitude value is not within the valid range.

        """
        if not -self.MAX_LONGITUDE <= value <= self.MAX_LONGITUDE:
            msglong = "Longitude must be between -180 and 180 degrees."
            raise ValueError(msglong)
        self._lon = value
