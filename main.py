"""
Adapted example of the vehicle routing problem with Google OR-Tools.
"""

import argparse

from ortools.constraint_solver import pywrapcp

from app.input import Input
from app.output import Output
from app.travel_duration import add_travel_duration_dimension
from app.unplanned import add_unplanned_penalty


def main():
    """Entry point for the program."""

    parser = argparse.ArgumentParser(description="Solve problems with OR-Tools.")
    parser.add_argument(
        "-input",
        default="",
        help="Path to input file. Default is stdin.",
    )
    parser.add_argument(
        "-output",
        default="",
        help="Path to output file. Default is stdout.",
    )
    parser.add_argument(
        "-duration",
        default=30,
        help="Max runtime duration (in seconds). Default is 30.",
        type=int,
    )
    parser.add_argument(
        "-max.travel.duration",
        default=86400,
        help="Max duration that a vehicle can travel for (in seconds). Default is 2700.",
        type=int,
        dest="max_travel_duration",
    )
    parser.add_argument(
        "-unplanned.penalty",
        default=50000,
        help="Penalty for dropping a stop.",
        type=int,
        dest="unplanned_penalty",
    )
    args = parser.parse_args()

    # Read input data, solve the problem and write the solution.
    input_data = Input.read(args.input)
    output = solve(input_data=input_data, args=args)
    output.write(args.output)


def solve(input_data: Input, args: argparse.Namespace) -> Output:
    """Solves the given problem and returns the solution."""

    # Create the routing index manager and model.
    manager = pywrapcp.RoutingIndexManager(
        len(input_data.stops) + 1,
        len(input_data.vehicles),
        0,
    )
    model = pywrapcp.RoutingModel(manager)

    # Add features to the model.
    add_travel_duration_dimension(
        manager=manager,
        model=model,
        input_data=input_data,
        max_travel_duration=args.max_travel_duration,
    )
    add_unplanned_penalty(
        manager=manager,
        model=model,
        input_data=input_data,
        unplanned_penalty=args.unplanned_penalty,
    )

    # Configure the solver.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.FromSeconds(args.duration)

    # Solve the problem.
    solution = model.SolveWithParameters(search_parameters)
    output = Output.from_solution(
        solution=solution,
        input_data=input_data,
        manager=manager,
        model=model,
    )

    return output


if __name__ == "__main__":
    main()
