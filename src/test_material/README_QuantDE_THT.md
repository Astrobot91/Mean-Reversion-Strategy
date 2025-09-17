
# Quantitative Data Engineer – Take-Home Test

Welcome! This is your take-home assignment for the **Quantitative Data Engineer – Trading Systems** role.  
You will build a small data processing and backtesting framework using the provided dataset.

---

## 📂 Provided Files
- `sample_tick_data.csv`: Simulated tick-level equity data (3 symbols, 1-second frequency, 1 trading day).  
  Columns: `timestamp, symbol, price, volume`

---

## 📝 Assignment Tasks

### Part 1: Market Data Processing
1. Read the CSV data.  
2. Resample ticks into **1-minute OHLCV bars**.  
3. Compute rolling indicators:  
   - 20-period moving average  
   - Volatility (standard deviation)  
4. Save results in an efficient format (e.g., Parquet).  

### Part 2: Trading Strategy Backtest
- Implement a **mean-reversion strategy**:  
  - Buy if price < (20-period MA − 1σ).  
  - Sell if price > (20-period MA + 1σ).  
- Constraints:  
  - Flat at market close.  
  - Commission: 0.01% per trade.  
- Output:  
  - PnL curve  
  - Win rate  
  - Sharpe ratio  

### Part 3: Risk & Stress Analysis
- Add risk controls:  
  - Max position size per symbol = 1,000 shares.  
  - Max daily loss = 2% of starting capital.  
- Add a stress test: shock all prices by −5% in a single day, recompute PnL.

### Part 4: AI Usage
- You may use AI tools (ChatGPT, Copilot, Claude, etc.).  
- Document in your report:  
  - Prompts you used  
  - AI outputs (snippets if relevant)  
  - What you accepted vs. changed  
  - Why you trusted or rejected AI output  

---

## 📦 Deliverables
Submit a **single zip file** with:  
1. `src/` → Your codebase (Python/Scala/C++/Rust/Java)  
2. `README.md` → Setup & run instructions  
3. `report.pdf` or `report.md` → including:  
   - System architecture & design  
   - Performance considerations  
   - Risk implementation  
   - AI usage documentation  
   - Next steps (how you’d scale to production with Databricks/AWS)  

---

## ⏱ Time Limit
- You have **48 hours** to submit once you start.  
- Expected effort: 4–6 hours of focused work.  
