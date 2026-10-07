"""SparkSession factory.

Centralising the session creation keeps every module and the notebook using the
same, consistent configuration.
"""
from __future__ import annotations

from .config import DEFAULT_CONFIG, PipelineConfig


def get_spark(config: PipelineConfig = DEFAULT_CONFIG):
    """Create (or reuse) a configured local SparkSession.

    Imports of ``pyspark`` happen inside the function so the rest of the package
    can be imported (and unit-tested) even on machines without Spark installed.
    """
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(config.app_name)
        .master(config.master)
        .config("spark.sql.shuffle.partitions", config.shuffle_partitions)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark
