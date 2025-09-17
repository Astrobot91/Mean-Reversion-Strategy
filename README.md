# Quantitative Data Engineer – Take-Home Test

## Setup & Run Instructions

### 1. Environment Setup
- Python 3.9+
- Create Virtual environment outside src folder after extracting
  ```bash
  python3 -m venv venv

  source venv/bin/activate

- Install dependencies:
  ```
  pip install -r requirements.txt
  ```


### 2. Project Structure
```
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_processing.py
│   │   ├── signals.py
│   │   ├── backtest.py
│   │   ├── config_loader.py
│   │   └── perf_metrics.py
│   └── data/
│       ├── tradesheets/
│       │   ├── unstressed_tradesheet.csv
│       │   └── stressed_tradesheet.csv
│       ├── plots/
│       │   ├── unstressed_pnl.png
│       │   ├── stressed_pnl.png
│       │   ├── unstressed_drawdown.png
│       │   └── stressed_drawdown.png
│       ├── metrics.csv
|       └── dataset.parquet
├── test-material/
│   └── sample_tick_data.csv
│       
├── README.md
├── requirements.txt
```

### 3. Usage

To run the full backtest pipeline (unstressed and stressed), save tradesheets, metrics, and plots, run:

```bash
PYTHONPATH=. python src/main.py
```
- Change the strategy configs in `src/config.yaml`
- Tradesheets will be saved in `src/data/tradesheets/`
- Metrics will be saved in `src/data/metrics.csv`
- Plots will be saved in `src/data/plots/`

### 4. Notes
- The code logic was first built in nuvama_test.ipynb.
- Then logic was modularized for clarity and reusability.
- For stress testing, a -5% price shock is applied and the full pipeline is rerun.
- See the notebook for full exploratory analysis and plotting examples.

