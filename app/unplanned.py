"""Unplanned module to handle penalties for dropping visits."""

from ortools.constraint_solver import pywrapcp

from app.input import Input


def add_unplanned_penalty(
    manager: pywrapcp.RoutingIndexManager,
    model: pywrapcp.RoutingModel,
    input_data: Input,
    unplanned_penalty: int,
) -> None:
    """Add the unplanned penalty as a disjunction to the routing problem."""

    for node in range(1, len(input_data.stops) + 1):
        model.AddDisjunction(
            [manager.NodeToIndex(node)],
            unplanned_penalty,
        )
