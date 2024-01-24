import argparse
import datetime
import json
import math
import sys
from typing import Any

import pyomo.environ as pyo

# Duration parameter for the solver.
SUPPORTED_PROVIDER_DURATIONS = {
    "cbc": "sec",
    "glpk": "tmlim",
}

# Status of the solver after optimizing.
STATUS = {
    pyo.TerminationCondition.feasible: "suboptimal",
    pyo.TerminationCondition.infeasible: "infeasible",
    pyo.TerminationCondition.optimal: "optimal",
    pyo.TerminationCondition.unbounded: "unbounded",
}


def main() -> None:
    """Entry point for the app."""

    parser = argparse.ArgumentParser(description="Solve shift-assignment with Pyomo.")
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
        "-provider",
        default="cbc",
        help="Solver provider. Default is cbc.",
    )
    args = parser.parse_args()

    # Read input data, solve the problem and write the solution.
    input_data = read_input(args.input)
    log("Solving shift-assignment:")
    log(f"  - shifts: {len(input_data.get('shifts', []))}")
    log(f"  - workers: {len(input_data.get('workers', []))}")
    log(f"  - rules: {len(input_data.get('rules', []))}")
    log(f"  - max duration: {args.duration} seconds")
    solution = solve(input_data, args.duration, args.provider)
    write_output(args.output, solution)


def solve(
    input_data: dict[str, Any],
    duration: int,
    provider: str,
) -> dict[str, Any]:
    """Solves the given problem and returns the solution."""

    # Measure the time.
    start_time = datetime.datetime.now()

    # Make sure the provider is supported.
    if provider not in SUPPORTED_PROVIDER_DURATIONS:
        raise ValueError(
            f"Unsupported provider: {provider}. The supported providers are: "
            f"{', '.join(SUPPORTED_PROVIDER_DURATIONS.keys())}"
        )

    # Creates the solver.
    solver = pyo.SolverFactory(provider)
    solver.options[SUPPORTED_PROVIDER_DURATIONS[provider]] = duration

    # Prepare data
    workers, shifts, rules_per_worker = convert_input(input_data)

    # >>> Variables

    # Create binary variables indicating whether a worker is assigned to a shift
    model = pyo.ConcreteModel()
    model.x_assign = pyo.Var(
        [(worker["id"], shift["id"]) for worker in workers for shift in shifts],
        within=pyo.Binary,
    )

    # >>> Objective

    # Maximize the sum of the preferences of the assigned shifts.
    preferences = sum(
        worker["preferences"].get(shift["id"], 0)
        * model.x_assign[(worker["id"], shift["id"])]
        for worker in workers
        for shift in shifts
    )
    model.objective = pyo.Objective(
        expr=preferences,
        sense=pyo.maximize,
    )

    # >>> Constraints

    # Each shift must have the required number of workers.
    for shift in shifts:
        num_workers = sum(model.x_assign[(e["id"], shift["id"])] for e in workers)
        model.add_component(
            f"shift_{shift['id']}_count",
            pyo.Constraint(expr=num_workers == shift["count"]),
        )

    # Each worker must be assigned the minimum and maximum number of shifts.
    for worker in workers:
        rules = rules_per_worker[worker["id"]]
        num_shifts = sum(model.x_assign[(worker["id"], s["id"])] for s in shifts)
        model.add_component(
            f"worker_{worker['id']}_min",
            pyo.Constraint(expr=num_shifts >= rules["min_shifts"]),
        )
        model.add_component(
            f"worker_{worker['id']}_max",
            pyo.Constraint(expr=num_shifts <= rules["max_shifts"]),
        )

    # Ensure that the minimum rest time between shifts is respected.
    for worker in workers:
        rest_time = datetime.timedelta(
            hours=rules_per_worker[worker["id"]]["min_rest_hours_between_shifts"]
        )
        for s1, shift1 in enumerate(shifts):
            for s2, shift2 in enumerate(shifts):
                if s1 >= s2:
                    continue

                if (
                    shift1["end_time"] + rest_time < shift2["start_time"]
                    or shift2["end_time"] + rest_time < shift1["start_time"]
                ):
                    continue

                # The two shifts are closer to each other than the minimum rest
                # time, so we need to ensure that the worker is not assigned to
                # both.
                assignment_1 = model.x_assign[(worker["id"], shift1["id"])]
                assignment_2 = model.x_assign[(worker["id"], shift2["id"])]
                expression = assignment_1 + assignment_2 <= 1
                model.add_component(
                    f"Rest_{worker['id']}_{shift1['id']}_{shift2['id']}",
                    pyo.Constraint(expr=expression),
                )

    # Ensure that availabilities are respected.
    for worker in workers:
        for shift in shifts:
            if not any(
                availability["start_time"] <= shift["start_time"]
                and availability["end_time"] >= shift["end_time"]
                for availability in worker["availability"]
            ):
                model.x_assign[(worker["id"], shift["id"])].fix(0)

    # Ensure that workers are qualified for the shift.
    for worker in workers:
        for shift in shifts:
            if "qualification" not in shift or shift["qualification"] == "":
                continue

            if "qualifications" not in worker:
                model.x_assign[(worker["id"], shift["id"])].fix(0)
                continue

            if shift["qualification"] not in worker["qualifications"]:
                model.x_assign[(worker["id"], shift["id"])].fix(0)

    # Solve the model.
    results = solver.solve(model)

    # Parse solution.
    assigned_shifts = []
    fixed_vars = 0
    for worker in workers:
        for shift in shifts:
            assignment = model.x_assign[(worker["id"], shift["id"])]
            if assignment() is not None and assignment() > 0.9:
                assigned_shifts.append(
                    {
                        "worker_id": worker["id"],
                        "shift_id": shift["id"],
                        "start_time": shift["start_time"],
                        "end_time": shift["end_time"],
                    }
                )
            if assignment.is_fixed():
                fixed_vars += 1

    active_workers = len(set(shift["worker_id"] for shift in assigned_shifts))
    total_workers = len(workers)

    try:
        value = pyo.value(model.objective)
    except ValueError:
        value = math.nan

    # Measure the time.
    end_time = datetime.datetime.now()

    # Creates the statistics.
    statistics = {
        "result": {
            "custom": {
                "provider": provider,
                "status": STATUS.get(results.solver.termination_condition, "unknown"),
                "variables": model.nvariables(),
                "fixed_variables": fixed_vars,
                "constraints": model.nconstraints(),
                "active_workers": active_workers,
                "total_workers": total_workers,
                "availability_usage": 100 * (active_workers / total_workers),
            },
            "duration": results.solver.time,
            "value": value,
        },
        "run": {
            "duration": (end_time - start_time).total_seconds(),
        },
        "schema": "v1",
    }

    return {
        "solutions": [{"assigned_shifts": assigned_shifts}],
        "statistics": statistics,
    }


def convert_input(input_data: dict[str, Any]) -> tuple[list, list, dict]:
    """Converts the input data to the format expected by the model."""
    workers = input_data["workers"]
    shifts = input_data["shifts"]

    # In-place convert timestamps to datetime objects
    for s in shifts:
        s["start_time"] = datetime.datetime.fromisoformat(s["start_time"])
        s["end_time"] = datetime.datetime.fromisoformat(s["end_time"])
    for e in workers:
        for a in e["availability"]:
            a["start_time"] = datetime.datetime.fromisoformat(a["start_time"])
            a["end_time"] = datetime.datetime.fromisoformat(a["end_time"])

    # Add default values for rules
    for r in input_data["rules"]:
        r["min_shifts"] = r.get("min_shifts", 0)
        r["max_shifts"] = r.get("max_shifts", 1000)

    # Add default values for workers
    for e in workers:
        e["preferences"] = e.get("preferences", {})

    # Merge availabilities of workers that start right where another one ends
    for e in workers:
        e["availability"] = sorted(e["availability"], key=lambda x: x["start_time"])
        i = 0
        while i < len(e["availability"]) - 1:
            if (
                e["availability"][i]["end_time"]
                == e["availability"][i + 1]["start_time"]
            ):
                e["availability"][i]["end_time"] = e["availability"][i + 1]["end_time"]
                del e["availability"][i + 1]
            else:
                i += 1

    # Convert rules to dict
    rules_per_worker = {}
    for e in workers:
        rule = [r for r in input_data.get("rules", {}) if r["id"] == e["rules"]]
        if len(rule) != 1:
            raise ValueError(f"Invalid rule for worker {e['id']}")
        rules_per_worker[e["id"]] = rule[0]

    return workers, shifts, rules_per_worker


def custom_serial(obj):
    """JSON serializer for objects not serializable by default serializer."""
    if isinstance(obj, (datetime.datetime | datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def log(message: str) -> None:
    """Logs a message. We need to use stderr since stdout is used for the solution."""
    print(message, file=sys.stderr)


def read_input(input_path) -> dict[str, Any]:
    """Reads the input from stdin or a given input file."""
    input_file = {}
    if input_path:
        with open(input_path, encoding="utf-8") as file:
            input_file = json.load(file)
    else:
        input_file = json.load(sys.stdin)
    return input_file


def write_output(output_path, output) -> None:
    """Writes the output to stdout or a given output file."""
    content = json.dumps(output, indent=2, default=custom_serial)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content + "\n")
    else:
        print(content)


if __name__ == "__main__":
    main()
