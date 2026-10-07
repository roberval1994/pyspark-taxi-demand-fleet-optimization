"""Feature engineering in Spark SQL.

The core transformation turns millions of individual trips into a compact
**zone-hour demand table**: for each pickup zone and each hour, how many trips
started. On top of that we add calendar features that drive demand.
"""
from __future__ import annotations

from . import config as C


def build_zone_hour_demand(df):
    """Aggregate trips into a (zone, hour-bucket) demand table.

    Returns a DataFrame with one row per (zone, hourly timestamp) and a
    ``demand`` column = number of trips that started there in that hour.
    """
    from pyspark.sql import functions as F

    hourly = df.withColumn(
        "pickup_hour", F.date_trunc("hour", F.col(C.COL_PICKUP_TS))
    )

    demand = (
        hourly.groupBy(F.col(C.COL_PU_ZONE).alias("zone"), F.col("pickup_hour"))
        .agg(F.count(F.lit(1)).alias("demand"))
    )
    return demand


def add_calendar_features(demand_df):
    """Add hour-of-day, day-of-week and weekend flag to the demand table.

    These are the main cyclical drivers of taxi demand (rush hours, weekends).
    """
    from pyspark.sql import functions as F

    return (
        demand_df.withColumn("hour", F.hour("pickup_hour"))
        .withColumn("dayofweek", F.dayofweek("pickup_hour"))
        .withColumn(
            "is_weekend",
            F.when(F.dayofweek("pickup_hour").isin(1, 7), 1).otherwise(0),
        )
    )


def assemble_features(df, feature_cols: list[str]):
    """Assemble the given columns into a single MLlib ``features`` vector."""
    from pyspark.ml.feature import VectorAssembler

    assembler = VectorAssembler(
        inputCols=feature_cols, outputCol="features", handleInvalid="skip"
    )
    return assembler.transform(df)


# Columns fed to the model.
FEATURE_COLUMNS = ["zone", "hour", "dayofweek", "is_weekend"]
