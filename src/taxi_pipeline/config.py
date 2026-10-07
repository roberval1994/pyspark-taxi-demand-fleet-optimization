"""Central configuration for the taxi demand + fleet-optimization pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --- Paths ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Dataset --------------------------------------------------------------
# NYC TLC Trip Records are published as monthly Parquet files. Example:
#   https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
# The files are large; the pipeline reads whatever Parquet lives in data/raw/.
TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def tlc_monthly_url(service: str, year: int, month: int) -> str:
    """Return the download URL for one month of TLC trip data.

    ``service`` is e.g. ``"yellow"`` or ``"green"``.
    """
    return f"{TLC_BASE_URL}/{service}_tripdata_{year:04d}-{month:02d}.parquet"


# Column names in the yellow-taxi schema used by this pipeline.
COL_PICKUP_TS = "tpep_pickup_datetime"
COL_DROPOFF_TS = "tpep_dropoff_datetime"
COL_PU_ZONE = "PULocationID"
COL_DO_ZONE = "DOLocationID"
COL_TRIP_DISTANCE = "trip_distance"


@dataclass(frozen=True)
class PipelineConfig:
    """Tunable settings for the whole pipeline."""

    # Spark
    app_name: str = "taxi-demand-fleet-optimization"
    master: str = "local[*]"            # run locally using all cores
    shuffle_partitions: int = 64

    # Data hygiene
    min_trip_distance: float = 0.1      # drop zero/negative-distance trips
    max_trip_distance: float = 100.0    # drop absurd outliers (miles)
    min_passengers: int = 1

    # Modelling
    seed: int = 42
    test_fraction: float = 0.2          # chronological hold-out

    # Optimization
    fleet_size: int = 500               # vehicles available to allocate
    min_vehicles_per_zone: int = 0
    max_vehicles_per_zone: int = 60


DEFAULT_CONFIG = PipelineConfig()
