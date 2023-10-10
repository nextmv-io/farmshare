"""Input data for the application."""

import json
import sys
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Location:
    """A location on the map."""

    lon: float
    lat: float

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]):
        """Parses the location from a dictionary."""

        if obj is None:
            return None

        return cls(
            lon=obj["lon"],
            lat=obj["lat"],
        )


@dataclass
class Stop:
    """A stop corresponding to a customer request."""

    id: str
    location: Location

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> "Stop":
        """Parses the stop from a dictionary."""
        return cls(
            id=obj["id"],
            location=Location.from_dict(obj["location"]),
        )


@dataclass
class Vehicle:
    """A vehicle that can service stops."""

    id: str
    speed: float

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]):
        """Parses the vehicle from a dictionary."""
        return cls(
            id=obj["id"],
            speed=obj["speed"],
        )


@dataclass
class Input:
    """The input data."""

    depot: Stop
    vehicles: list[Vehicle]
    stops: list[Stop]
    stops_by_index: Dict[int, Stop] = None
    vehicles_by_index: Dict[int, Vehicle] = None

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]):
        """Parses the input from a dictionary."""

        stops_by_index = {}
        stops = []
        for ix, stop_obj in enumerate(obj["stops"]):
            stop = Stop.from_dict(stop_obj)
            stops.append(stop)
            stops_by_index[ix] = stop

        vehicles_by_index = {}
        vehicles = []
        for ix, vehicle_obj in enumerate(obj["vehicles"]):
            vehicle = Vehicle.from_dict(vehicle_obj)
            vehicles.append(vehicle)
            vehicles_by_index[ix] = vehicle

        return cls(
            depot=Stop.from_dict(obj["depot"]),
            vehicles=vehicles,
            stops=stops,
            stops_by_index=stops_by_index,
            vehicles_by_index=vehicles_by_index,
        )

    @classmethod
    def read(cls, input_path: str):
        """Reads the input from stdin or a given input file."""
        input_file = {}
        if input_path:
            with open(input_path, "r", encoding="utf-8") as file:
                input_file = json.load(file)
        else:
            input_file = json.load(sys.stdin)

        return cls.from_dict(input_file)

    def get_stop_by_index(self, index: int) -> Stop:
        """Returns a stop by its index."""

        if index == 0:
            return self.depot

        return self.stops_by_index[index - 1]
