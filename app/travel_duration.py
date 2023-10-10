"""Travel time module for calculating how a vehicle travels."""

import numpy as np
from ortools.constraint_solver import pywrapcp

from app.input import Input


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
    travel_dimension = model.AddDimensionWithVehicleTransits(
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

    lats_origin = np.array([input_data.depot.location.lat])
    lngs_origin = np.array([input_data.depot.location.lon])
    for stop in input_data.stops:
        lats_origin = np.append(lats_origin, stop.location.lat)
        lngs_origin = np.append(lngs_origin, stop.location.lon)

    lats_destination = np.copy(lats_origin)
    lngs_destination = np.copy(lngs_origin)

    # Create the combination of all origins and destinations.
    lats_origin = np.repeat(lats_origin, len(lats_destination))
    lngs_origin = np.repeat(lngs_origin, len(lngs_destination))
    lats_destination = np.tile(lats_destination, len(lats_destination))
    lngs_destination = np.tile(lngs_destination, len(lngs_destination))

    distances = haversine(
        lats_origin=lats_origin,
        lngs_origin=lngs_origin,
        lats_destination=lats_destination,
        lngs_destination=lngs_destination,
    )

    # Convert the distances to a square matrix.
    num_locations = len(input_data.stops) + 1
    matrix = distances.reshape(num_locations, num_locations)

    return matrix


def haversine(
    lats_origin: np.ndarray | float,
    lngs_origin: np.ndarray | float,
    lats_destination: np.ndarray | float,
    lngs_destination: np.ndarray | float,
) -> np.ndarray | float:
    """Calculates the haversine distance between arrays of coordinates."""

    lngs_destination, lats_destination, lngs_origin, lats_origin = map(
        np.radians,
        [lngs_destination, lats_destination, lngs_origin, lats_origin],
    )
    delta_lon = lngs_destination - lngs_origin
    delta_lat = lats_destination - lats_origin
    term1 = np.sin(delta_lat / 2.0) ** 2
    term2 = np.cos(lats_origin) * np.cos(lats_destination) * np.sin(delta_lon / 2.0) ** 2
    a = term1 + term2
    c = 2 * np.arcsin(np.sqrt(a))

    return 6371000 * c
