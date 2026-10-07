"""Ingestion and cleaning of NYC TLC trip records.

Reads the monthly Parquet files from ``data/raw/`` as a Spark DataFrame and
applies basic data-quality filters. All transformations are lazy: nothing is
computed until an action (``count``, ``write``, ...) is triggered downstream.
"""
from __future__ import annotations

from .config import DEFAULT_CONFIG, PipelineConfig
from . import config as C


def read_trips(spark, path: str | None = None):
    """Read all Parquet trip files under ``path`` (default: ``data/raw/``)."""
    path = path or str(C.RAW_DIR)
    return spark.read.parquet(path)


def clean_trips(df, config: PipelineConfig = DEFAULT_CONFIG):
    """Apply data-quality filters to the raw trip DataFrame.

    Removes trips with implausible distance, non-positive passenger counts and
    null pickup zones/timestamps. Returns a lazily-transformed DataFrame.
    """
    from pyspark.sql import functions as F

    cleaned = (
        df.filter(F.col(C.COL_TRIP_DISTANCE) >= config.min_trip_distance)
        .filter(F.col(C.COL_TRIP_DISTANCE) <= config.max_trip_distance)
        .filter(F.col(C.COL_PU_ZONE).isNotNull())
        .filter(F.col(C.COL_PICKUP_TS).isNotNull())
    )

    # ``passenger_count`` is optional in some vintages of the schema.
    if "passenger_count" in df.columns:
        cleaned = cleaned.filter(
            F.col("passenger_count") >= config.min_passengers
        )

    return cleaned
