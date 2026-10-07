"""End-to-end runner: Spark demand model -> fleet allocation.

Usage:
    python scripts/run_pipeline.py

Requires a running Spark environment and at least one NYC TLC Parquet file in
``data/raw/`` (see data/README.md for how to download one). Writes the demand
metrics and the fleet-allocation plan to ``outputs/``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from taxi_pipeline import config, features, ingest, model, optimize  # noqa: E402
from taxi_pipeline.spark_session import get_spark  # noqa: E402


def main() -> None:
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    spark = get_spark()

    print("[1/5] Reading & cleaning trips ...")
    trips = ingest.clean_trips(ingest.read_trips(spark))

    print("[2/5] Building zone-hour demand table ...")
    demand = features.add_calendar_features(features.build_zone_hour_demand(trips))

    print("[3/5] Training demand model (Spark MLlib GBT) ...")
    train, test, cutoff = model.chronological_split(demand)
    fitted = model.train_demand_model(train)
    metrics = model.evaluate_model(fitted, test)
    print("    metrics:", metrics)
    (config.OUTPUTS_DIR / "demand_metrics.json").write_text(json.dumps(metrics, indent=2))

    print("[4/5] Forecasting demand per zone for the next hour ...")
    # Aggregate predicted demand by zone on the test horizon.
    from pyspark.sql import functions as F
    from taxi_pipeline.features import FEATURE_COLUMNS, assemble_features

    scored = fitted.transform(assemble_features(test, FEATURE_COLUMNS))
    by_zone = (
        scored.groupBy("zone")
        .agg(F.sum(F.greatest(F.col("prediction"), F.lit(0.0))).alias("pred_demand"))
        .orderBy(F.desc("pred_demand"))
        .limit(50)  # focus on the 50 busiest zones for the demo
    )
    demand_by_zone = {int(r["zone"]): float(r["pred_demand"]) for r in by_zone.collect()}

    print("[5/5] Optimizing fleet allocation (ILP) ...")
    exact = optimize.allocate_fleet(demand_by_zone)
    heur = optimize.greedy_baseline(demand_by_zone)
    print(f"    exact  coverage = {exact.coverage:.1%} (status={exact.status})")
    print(f"    greedy coverage = {heur.coverage:.1%}")

    (config.OUTPUTS_DIR / "fleet_allocation.json").write_text(
        json.dumps(
            {
                "exact": {"coverage": exact.coverage, "allocation": exact.allocation},
                "greedy": {"coverage": heur.coverage, "allocation": heur.allocation},
            },
            indent=2,
        )
    )

    print(f"\nDone. Artifacts in: {config.OUTPUTS_DIR}")
    spark.stop()


if __name__ == "__main__":
    main()
