"""Demand model with Spark MLlib.

Trains a Gradient-Boosted Trees regressor to predict hourly demand per zone and
evaluates it on a chronological hold-out, mirroring the discipline used in the
single-machine project (no shuffling of time-ordered data).
"""
from __future__ import annotations

from .config import DEFAULT_CONFIG, PipelineConfig
from .features import FEATURE_COLUMNS, assemble_features


def chronological_split(demand_df, config: PipelineConfig = DEFAULT_CONFIG):
    """Split the demand table by time into (train, test) DataFrames.

    We compute the timestamp quantile that leaves the last ``test_fraction`` of
    the period as the test set — the distributed analogue of a time cut.
    """
    from pyspark.sql import functions as F

    bounds = demand_df.agg(
        F.min("pickup_hour").alias("tmin"), F.max("pickup_hour").alias("tmax")
    ).collect()[0]
    tmin, tmax = bounds["tmin"], bounds["tmax"]
    span = (tmax - tmin).total_seconds()
    cutoff_seconds = span * (1.0 - config.test_fraction)
    cutoff = tmin + __import__("datetime").timedelta(seconds=cutoff_seconds)

    train = demand_df.filter(F.col("pickup_hour") < F.lit(cutoff))
    test = demand_df.filter(F.col("pickup_hour") >= F.lit(cutoff))
    return train, test, cutoff


def train_demand_model(train_df, config: PipelineConfig = DEFAULT_CONFIG):
    """Fit a GBT regressor on the assembled training features."""
    from pyspark.ml.regression import GBTRegressor

    train_feat = assemble_features(train_df, FEATURE_COLUMNS)
    gbt = GBTRegressor(
        featuresCol="features",
        labelCol="demand",
        maxIter=50,
        maxDepth=5,
        seed=config.seed,
    )
    return gbt.fit(train_feat)


def evaluate_model(fitted_model, test_df) -> dict[str, float]:
    """Return RMSE, MAE and R2 of the model on the test set."""
    from pyspark.ml.evaluation import RegressionEvaluator

    test_feat = assemble_features(test_df, FEATURE_COLUMNS)
    preds = fitted_model.transform(test_feat)

    metrics = {}
    for name in ("rmse", "mae", "r2"):
        evaluator = RegressionEvaluator(
            labelCol="demand", predictionCol="prediction", metricName=name
        )
        metrics[name.upper()] = float(evaluator.evaluate(preds))
    return metrics


def predict_next_period(fitted_model, feature_rows):
    """Score a DataFrame of (zone, hour, dayofweek, is_weekend) rows.

    Used to produce the demand forecast that feeds the optimization step.
    Returns a DataFrame with a ``prediction`` column.
    """
    feat = assemble_features(feature_rows, FEATURE_COLUMNS)
    return fitted_model.transform(feat)
