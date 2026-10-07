"""Unit tests for the fleet-allocation optimization (no Spark required)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from taxi_pipeline import optimize  # noqa: E402
from taxi_pipeline.config import PipelineConfig  # noqa: E402


@pytest.fixture
def demand():
    """A small demand profile across five zones."""
    return {1: 300.0, 2: 150.0, 3: 80.0, 4: 40.0, 5: 10.0}


def test_allocation_respects_fleet_budget(demand):
    cfg = PipelineConfig(fleet_size=50, max_vehicles_per_zone=60)
    res = optimize.allocate_fleet(demand, trips_per_vehicle=10.0, config=cfg)
    assert sum(res.allocation.values()) <= cfg.fleet_size
    assert res.status == "Optimal"


def test_allocation_respects_zone_upper_bound(demand):
    cfg = PipelineConfig(fleet_size=1000, max_vehicles_per_zone=5)
    res = optimize.allocate_fleet(demand, trips_per_vehicle=10.0, config=cfg)
    assert all(v <= 5 for v in res.allocation.values())


def test_served_never_exceeds_demand(demand):
    cfg = PipelineConfig(fleet_size=1000, max_vehicles_per_zone=60)
    res = optimize.allocate_fleet(demand, trips_per_vehicle=10.0, config=cfg)
    for z, d in demand.items():
        assert res.served[z] <= d + 1e-6


def test_more_fleet_covers_at_least_as_much(demand):
    small = optimize.allocate_fleet(
        demand, config=PipelineConfig(fleet_size=10, max_vehicles_per_zone=60)
    )
    big = optimize.allocate_fleet(
        demand, config=PipelineConfig(fleet_size=60, max_vehicles_per_zone=60)
    )
    assert big.total_served >= small.total_served


def test_exact_beats_or_matches_greedy(demand):
    cfg = PipelineConfig(fleet_size=40, max_vehicles_per_zone=60)
    exact = optimize.allocate_fleet(demand, config=cfg)
    greedy = optimize.greedy_baseline(demand, config=cfg)
    # The exact ILP must never be worse than the heuristic.
    assert exact.total_served >= greedy.total_served - 1e-6


def test_coverage_is_a_fraction(demand):
    res = optimize.allocate_fleet(demand, config=PipelineConfig(fleet_size=20))
    assert 0.0 <= res.coverage <= 1.0
