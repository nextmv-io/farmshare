"""Output data for the application."""

import json
import math
from dataclasses import asdict, dataclass
from typing import List, Tuple

from ortools.constraint_solver import pywrapcp

from app.input import Input
from app.input import Stop as InputStop
from app.input import Vehicle as InputVehicle


@dataclass
class Custom:
    """The custom statistics."""

    activated_vehicles: int
    max_travel_duration: float
    min_travel_duration: float
    max_stops_in_vehicle: int
    min_stops_in_vehicle: int


@dataclass
class Result:
    """The result statistics."""

    custom: Custom
    duration: float
    value: float


@dataclass
class Run:
    """The run statistics."""

    duration: float


@dataclass
class Statistics:
    """The statistics of the run."""

    result: Result
    run: Run
    schema: str


@dataclass
class Stop:
    """The stop in a route."""

    stop: InputStop
    cumulative_travel_duration: float


@dataclass
class Vehicle:
    """The vehicle of the output."""

    id: str
    route: List[Stop]
    route_travel_duration: float


@dataclass
class Solution:
    """The solution of the problem."""

    unplanned: List[InputStop]
    vehicles: List[Vehicle]


def _build_vehicle(
    solution,
    travel_dimension: pywrapcp.RoutingDimension,
    model: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    vehicle: InputVehicle,
    vehicle_ix: int,
    input_data: Input,
) -> Tuple[Vehicle, int]:
    """Builds a vehicle from the solution and returns the vehicle and its
    travel duration."""

    index = model.Start(vehicle_ix)
    route = []
    while not model.IsEnd(index):
        stop = input_data.get_stop_by_index(index=manager.IndexToNode(index))
        travel_duration_var = travel_dimension.CumulVar(index)
        output_stop = Stop(
            stop=stop,
            cumulative_travel_duration=solution.Min(travel_duration_var),
        )
        route.append(output_stop)
        index = solution.Value(model.NextVar(index))

    stop = input_data.get_stop_by_index(index=manager.IndexToNode(index))
    travel_duration_var = travel_dimension.CumulVar(index)
    output_stop = Stop(
        stop=stop,
        cumulative_travel_duration=solution.Min(travel_duration_var),
    )
    route.append(output_stop)
    output_vehicle = Vehicle(
        id=vehicle.id,
        route=route,
        route_travel_duration=output_stop.cumulative_travel_duration,
    )

    return output_vehicle, output_stop.cumulative_travel_duration


@dataclass
class Output:
    """The output with the result."""

    solutions: list[Solution]
    statistics: Statistics

    def write(self, output_path: str) -> None:
        """Writes the output to stdout or a given output file."""
        content = json.dumps(asdict(self), indent=2)
        if output_path != "":
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(content + "\n")
        else:
            print(content)

    @classmethod
    def from_solution(
        cls,
        solution,
        input_data: Input,
        manager: pywrapcp.RoutingIndexManager,
        model: pywrapcp.RoutingModel,
    ):
        """Builds the class from the solution."""

        unplanned_stops = []
        for node in range(model.Size()):
            if model.IsStart(node) or model.IsEnd(node):
                continue
            if solution.Value(model.NextVar(node)) == node:
                index = manager.IndexToNode(node)
                unplanned_stops.append(input_data.get_stop_by_index(index))

        output_vehicles = []
        activated_vehicles = 0
        max_travel_duration = 0
        min_travel_duration = math.inf
        max_stops_in_vehicle = 0
        min_stops_in_vehicle = len(input_data.stops)
        travel_dimension = model.GetDimensionOrDie("travel_duration")
        for vehicle_ix, vehicle in enumerate(input_data.vehicles):
            output_vehicle, travel_duration = _build_vehicle(
                solution=solution,
                travel_dimension=travel_dimension,
                model=model,
                manager=manager,
                vehicle=vehicle,
                vehicle_ix=vehicle_ix,
                input_data=input_data,
            )
            output_vehicles.append(output_vehicle)

            route = output_vehicle.route
            if len(route) > 2:
                activated_vehicles += 1
                max_travel_duration = max(max_travel_duration, travel_duration)
                min_travel_duration = min(min_travel_duration, travel_duration)
                max_stops_in_vehicle = max(max_stops_in_vehicle, len(route) - 2)
                min_stops_in_vehicle = min(min_stops_in_vehicle, len(route) - 2)

        duration = solution.solver().WallTime() / 1000
        statistics = Statistics(
            result=Result(
                custom=Custom(
                    activated_vehicles=activated_vehicles,
                    max_travel_duration=max_travel_duration,
                    min_travel_duration=min_travel_duration,
                    max_stops_in_vehicle=max_stops_in_vehicle,
                    min_stops_in_vehicle=min_stops_in_vehicle,
                ),
                duration=duration,
                value=solution.ObjectiveValue(),
            ),
            run=Run(duration=duration),
            schema="v1",
        )

        return cls(
            solutions=[
                Solution(
                    vehicles=output_vehicles,
                    unplanned=unplanned_stops,
                ),
            ],
            statistics=statistics,
        )
