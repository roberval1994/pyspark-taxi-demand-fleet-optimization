"""Fleet allocation as an optimization problem (Operational Research).

The ML stage gives us a *forecast* of demand per zone. This stage turns that
forecast into a *decision*: how many vehicles to station in each zone, given a
limited fleet, so that we cover as much expected demand as possible.

Formulation (Integer Linear Program)
------------------------------------
Decision variables
    x_z  = number of vehicles allocated to zone z   (integer, >= 0)
    s_z  = demand served in zone z                  (continuous, >= 0)

Each vehicle serves up to ``trips_per_vehicle`` trips in the horizon, so the
served demand in a zone cannot exceed either the predicted demand or the
capacity provided by its vehicles.

    maximize    sum_z s_z
    subject to  sum_z x_z <= fleet_size
                s_z <= demand_z
                s_z <= trips_per_vehicle * x_z
                lb <= x_z <= ub

This is a transportation/covering-style allocation, solved exactly with the CBC
solver bundled with PuLP.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import DEFAULT_CONFIG, PipelineConfig


@dataclass
class AllocationResult:
    """Outcome of the fleet-allocation optimization."""

    allocation: dict[int, int]      # zone -> vehicles
    served: dict[int, float]        # zone -> expected demand served
    total_served: float
    total_demand: float
    status: str

    @property
    def coverage(self) -> float:
        """Fraction of total predicted demand that is covered."""
        return self.total_served / self.total_demand if self.total_demand else 0.0


def allocate_fleet(
    demand_by_zone: dict[int, float],
    trips_per_vehicle: float = 10.0,
    config: PipelineConfig = DEFAULT_CONFIG,
) -> AllocationResult:
    """Allocate a fixed fleet across zones to maximize covered demand.

    Parameters
    ----------
    demand_by_zone:
        Mapping ``zone -> predicted demand`` (e.g. produced by the ML model).
    trips_per_vehicle:
        How many trips one vehicle can serve in the planning horizon.
    config:
        Provides ``fleet_size`` and per-zone bounds.
    """
    import pulp

    zones = list(demand_by_zone.keys())

    problem = pulp.LpProblem("fleet_allocation", pulp.LpMaximize)

    x = {
        z: pulp.LpVariable(
            f"x_{z}",
            lowBound=config.min_vehicles_per_zone,
            upBound=config.max_vehicles_per_zone,
            cat="Integer",
        )
        for z in zones
    }
    s = {z: pulp.LpVariable(f"s_{z}", lowBound=0) for z in zones}

    # Objective: maximize total served demand.
    problem += pulp.lpSum(s[z] for z in zones)

    # Fleet-size budget.
    problem += pulp.lpSum(x[z] for z in zones) <= config.fleet_size

    # Served demand bounded by predicted demand and by provided capacity.
    for z in zones:
        problem += s[z] <= demand_by_zone[z]
        problem += s[z] <= trips_per_vehicle * x[z]

    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    allocation = {z: int(round(x[z].value() or 0)) for z in zones}
    served = {z: float(s[z].value() or 0.0) for z in zones}
    total_served = sum(served.values())
    total_demand = sum(demand_by_zone.values())

    return AllocationResult(
        allocation=allocation,
        served=served,
        total_served=total_served,
        total_demand=total_demand,
        status=pulp.LpStatus[problem.status],
    )


def greedy_baseline(
    demand_by_zone: dict[int, float],
    trips_per_vehicle: float = 10.0,
    config: PipelineConfig = DEFAULT_CONFIG,
) -> AllocationResult:
    """A simple proportional heuristic, to benchmark the exact model against.

    Allocates vehicles proportionally to each zone's share of total demand,
    capped by the per-zone upper bound. Useful to show that the exact ILP does
    at least as well as an intuitive rule of thumb.
    """
    total_demand = sum(demand_by_zone.values())
    allocation: dict[int, int] = {}
    remaining = config.fleet_size

    # Proportional first pass.
    for z, d in sorted(demand_by_zone.items(), key=lambda kv: kv[1], reverse=True):
        share = (d / total_demand) if total_demand else 0.0
        want = int(share * config.fleet_size)
        give = max(config.min_vehicles_per_zone, min(want, config.max_vehicles_per_zone, remaining))
        allocation[z] = give
        remaining -= give

    served = {
        z: min(demand_by_zone[z], trips_per_vehicle * allocation[z])
        for z in demand_by_zone
    }
    total_served = sum(served.values())

    return AllocationResult(
        allocation=allocation,
        served=served,
        total_served=total_served,
        total_demand=total_demand,
        status="heuristic",
    )
