"""Distributed demand forecasting + fleet optimization for NYC taxi data.

This package combines two disciplines on a large, public dataset (NYC TLC Trip
Records):

1. **Machine Learning at scale** with PySpark / Spark MLlib — predict taxi
   demand per zone and hour.
2. **Operational Research** — turn those predictions into a decision: how to
   allocate / rebalance a limited fleet across zones to best meet demand.

The story is deliberately end-to-end: *forecast, then decide*.

Modules
-------
- ``spark_session`` : build and configure the SparkSession.
- ``ingest``        : read and clean the raw trip records.
- ``features``      : build the zone-hour demand table and ML features.
- ``model``         : train/evaluate a Spark MLlib demand model.
- ``optimize``      : allocate a fleet across zones from the predicted demand.
"""

__version__ = "1.0.0"
__author__ = "Roberval Goncalves Moreira Filho"
