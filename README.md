<h1 align="center">🚕 NYC Taxi — Distributed Demand Forecasting & Fleet Optimization</h1>

<p align="center">
  <b>Big-data Machine Learning (PySpark) meets Operational Research</b><br>
  Forecast demand per zone with Spark MLlib, then <i>decide</i> how to allocate a fleet with an exact optimization model.
</p>

🌐 **Language / Idioma:** **English** | [Português](README.pt-BR.md)

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.4%2B-E25A1C.svg?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Solver](https://img.shields.io/badge/Optimization-PuLP%20%2F%20CBC-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 What this project shows

Two skills that rarely appear together, applied to one realistic problem:

1. **Machine Learning at scale** — using **PySpark / Spark MLlib** to process millions of
   NYC taxi trips and predict hourly demand per zone.
2. **Operational Research** — turning that forecast into an **actionable decision**: an
   exact Integer Linear Program (ILP) that allocates a limited fleet across zones to
   maximize covered demand.

The narrative is **forecast → decide**: a prediction is only useful if it drives a better
decision. This mirrors real logistics work (fleet positioning, resource allocation).

## 💼 Business context & impact

**Problem.** A ride-hailing / taxi operator has a *limited fleet* and *uneven demand*
across a city. Put too many cars where demand is low and you burn idle capacity; too few
where demand is high and you lose rides. The question is operational: **where should each
vehicle be?**

**Who benefits.** Operations (fleet positioning), revenue teams (fewer lost rides), and
drivers (less idle time).

**Measured results.** On the forecasted demand, with a fleet of 40 vehicles over the 50
busiest zones, the **exact optimization covered ~69% of demand vs. ~64% for a proportional
greedy rule** — a ~5-point gain in coverage from the same fleet, purely by deciding
allocation optimally.

> 💡 *Illustrative business framing:* those extra coverage points are rides that would
> otherwise be lost. At city scale and repeated every hour, optimal allocation compounds
> into materially better service and revenue from the **same** number of vehicles.

## 🧠 Technical decisions & trade-offs

| Decision | Why | Trade-off considered |
|---|---|---|
| **PySpark** instead of pandas | Millions of trips per month, growing with every added month; the same code scales from laptop to cluster | Spark needs a JVM and has startup overhead — only worth it at this data volume |
| **Parquet** as the data format | Columnar + compressed → reads only the needed columns, far faster than CSV | Binary (not human-readable) — a fair trade for analytics |
| **Exact ILP (PuLP/CBC)** for allocation | Provably optimal coverage; auditable decision | Scales worse than heuristics on huge instances — benchmarked against a greedy baseline to prove the gain is real |
| **Greedy baseline kept alongside** | Honest comparison: shows the exact model actually earns its complexity | Extra code — but it is exactly what a decision-maker asks for |
| **Lazy Spark imports** | The package imports and the OR tests run even without Spark installed | A little indirection in the code — worth it for testability |

## 🗺️ Pipeline overview

```
 NYC TLC trips (Parquet, millions of rows)
        │   PySpark: read + clean
        ▼
 Zone–hour demand table  ──►  Spark MLlib (GBT regressor)  ──►  demand forecast per zone
        │                                                             │
        │                                              Operational Research (PuLP / CBC)
        ▼                                                             ▼
   calendar features                                   exact fleet allocation + baseline
```

## 🗂️ Project structure

```
pyspark-taxi-demand-fleet-optimization/
├── data/
│   └── raw/                     # NYC TLC Parquet files (not versioned)
├── notebooks/
│   └── 00_walkthrough.ipynb     # Guided, documented end-to-end tour
├── src/taxi_pipeline/
│   ├── config.py                # Paths, dataset URLs, tunable parameters
│   ├── spark_session.py         # SparkSession factory
│   ├── ingest.py                # Read & clean trip records (Spark)
│   ├── features.py              # Zone-hour demand table + calendar features (Spark)
│   ├── model.py                 # Spark MLlib demand model (train/evaluate)
│   └── optimize.py              # Fleet allocation ILP + greedy baseline (PuLP)
├── scripts/
│   └── run_pipeline.py          # One-command end-to-end run
├── tests/
│   └── test_optimize.py         # Unit tests for the optimization (no Spark needed)
├── requirements.txt
├── LICENSE
├── README.md                    # English (this file)
└── README.pt-BR.md              # Portuguese
```

## 🔬 Pipeline stages

| Stage | Module | What it does |
|---|---|---|
| **1. Ingest** | `ingest.py` | Reads monthly Parquet files, applies data-quality filters |
| **2. Features** | `features.py` | Aggregates trips into a zone-hour demand table; adds calendar features |
| **3. Model** | `model.py` | Trains a Spark MLlib **GBT** regressor; chronological evaluation (RMSE/MAE/R²) |
| **4. Forecast** | `model.py` | Predicts demand per zone for the planning horizon |
| **5. Optimize** | `optimize.py` | **Exact ILP** allocates the fleet; compared against a greedy baseline |

## ⚡ Quick start

```bash
git clone https://github.com/roberval1994/pyspark-taxi-demand-fleet-optimization.git
cd pyspark-taxi-demand-fleet-optimization

python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Download at least one month of data into data/raw/ (see data/README.md), then:
python scripts/run_pipeline.py
```

> **Spark requirement:** PySpark needs a Java runtime (JDK 8/11/17). On Windows, Anaconda
> makes this easy. The **optimization module and its tests run without Spark**.

## 🧪 Tests

```bash
pytest -q
```

The optimization is covered by unit tests — including a check that the **exact ILP never
performs worse than the greedy heuristic**, and that fleet-budget and per-zone capacity
constraints are respected.

## 📈 Example result

On a sample demand profile, with a fleet of 40 vehicles, the **exact ILP covered ~69%** of
predicted demand versus **~64%** for the proportional greedy rule — the kind of margin that
matters at city scale.

## 🧰 Tech stack

`PySpark` · `Spark MLlib` · `PuLP` (CBC) · `pandas` · `NumPy` · `Matplotlib` · `pytest`

## 📚 Design principles

- **Scales down gracefully**: Spark imports are lazy, so the package imports and the OR
  tests run even without Spark installed.
- **No temporal leakage**: the demand model is evaluated on a chronological hold-out.
- **Forecast feeds decision**: the ML output is the optimizer's input — one coherent story.
- **Exact vs. heuristic**: the ILP is benchmarked against a baseline, as in real OR work.

## 👤 Author

**Roberval Gonçalves Moreira Filho** — Data Scientist | Operational Research Analyst

[![LinkedIn](https://img.shields.io/badge/LinkedIn-robervalOr-blue)](https://www.linkedin.com/in/robervalOr)
[![Lattes](https://img.shields.io/badge/Lattes-CNPq-00599C)](http://lattes.cnpq.br/4394523940603239)
[![GitHub](https://img.shields.io/badge/GitHub-roberval1994-black)](https://github.com/roberval1994)

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE).
