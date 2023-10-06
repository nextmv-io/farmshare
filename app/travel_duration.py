"""Travel time module for calculating how a vehicle travels."""

import numpy as np
from ortools.constraint_solver import pywrapcp

from app.input import Input, Location


def add_travel_duration_dimension(
    manager: pywrapcp.RoutingIndexManager,
    model: pywrapcp.RoutingModel,
    input_data: Input,
):
    """Add the travel time as a dimension to the routing problem."""

    matrix = distance_matrix(input_data)

    def travel_by_vehicle_callback(vehicle_ix: int):
        def travel_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            vehicle = input_data.vehicles_by_index[vehicle_ix]
            travel_duration = matrix[from_node][to_node] / vehicle.speed

            # The travel duration must be an int.
            return int(travel_duration)

        return travel_callback

    transit_callback_indices = []
    for ix in range(len(input_data.vehicles)):
        transit_callback = travel_by_vehicle_callback(ix)
        transit_callback_indices.append(model.RegisterTransitCallback(transit_callback))

    dimension_name = "travel_duration"
    model.AddDimensionWithVehicleTransits(
        evaluator_indices=transit_callback_indices,
        slack_max=0,
        capacity=24 * 3600,
        fix_start_cumul_to_zero=True,
        name=dimension_name,
    )
    travel_dimension = model.GetDimensionOrDie(dimension_name)
    travel_dimension.SetGlobalSpanCostCoefficient(100)


def distance_matrix(input_data: Input) -> np.ndarray:
    """Calculates the distance matrix for the input data."""

    locations = [input_data.depot.location] + [stop.location for stop in input_data.stops]
    num_locations = len(locations)
    matrix = np.zeros((num_locations, num_locations))
    for i in range(num_locations):
        for j in range(num_locations):
            matrix[i, j] = haversine(location1=locations[i], location2=locations[j])

    return matrix


def haversine(location1: Location, location2: Location) -> float:
    """Calculates the distance between two locations using the Haversine
    formula."""

    radius = 6371000
    lat1, lon1 = np.radians([location1.lat, location1.lon])
    lat2, lon2 = np.radians([location2.lat, location2.lon])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return radius * c
