import os
import polars as pl
import matplotlib.pyplot as plt
import pandas as pd
from src.services.data_processing import load_and_resample_data, save_parquet
from src.services.signals import generate_signals
from src.services.backtest import run_backtest, BacktestParams
from src.services.config_loader import load_strategy_config
from src.services.perf_metrics import calculate_performance_metrics, calculate_drawdowns


def main():
    # Load the sample data, resample and create the necessary features
    print("Loading and processing data...")
    sample_data = load_and_resample_data('src/test_material/sample_tick_data.csv')
    data_path = os.path.join('src', 'data')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    save_parquet(sample_data, os.path.join('src', 'data', 'dataset.parquet'))


    # Generate signals
    print("Generating signals...")
    backtest_data = generate_signals(sample_data)

    # Load strategy parameters from config
    print("Loading strategy configuration...")
    config = load_strategy_config(os.path.join('src', 'config.yaml'), 'MeanReversion')
    params = BacktestParams.from_dict(config)

    # Run unstressed backtest
    print("Running unstressed backtest...")
    trades_df = run_backtest(backtest_data, params)
    tradesheet_dir = os.path.join('src', 'data', 'tradesheets')
    if not os.path.exists(tradesheet_dir):
        os.makedirs(tradesheet_dir)
    trades_df.write_csv(os.path.join(tradesheet_dir, 'unstressed_tradesheet.csv'))
    print("Unstressed tradesheet saved at:", os.path.join(tradesheet_dir, 'unstressed_tradesheet.csv'))

    # Stress Test - Shock the stocks by 5%
    stress_data = backtest_data.clone()
    print("Running stressed backtest with 5% shock...")
    stress_data = stress_data.with_columns([
        (pl.col("open") * (1 + params.shock_percentage)).alias("open"),
        (pl.col("high") * (1 + params.shock_percentage)).alias("high"),
        (pl.col("low") * (1 - params.shock_percentage)).alias("low"),
        (pl.col("close") * (1 - params.shock_percentage)).alias("close")
    ]).with_columns([
        pl.col("close").rolling_mean(window_size=params.window_size).over("symbol").alias("sma_20"),
        pl.col("close").rolling_std(window_size=params.window_size).over("symbol").alias("std_dev_1")
    ])
    stress_data = generate_signals(stress_data)
    stressed_trades_df = run_backtest(stress_data, params)
    stressed_trades_df.write_csv(os.path.join(tradesheet_dir, 'stressed_tradesheet.csv'))
    print("Stressed tradesheet saved at:", os.path.join(tradesheet_dir, 'stressed_tradesheet.csv'))

    # Metrics and Plots
    metrics_unstressed = calculate_performance_metrics(trades_df)
    metrics_stressed = calculate_performance_metrics(stressed_trades_df)
    metrics_df = pd.DataFrame([
        {'Scenario': 'Unstressed', **metrics_unstressed},
        {'Scenario': 'Stressed', **metrics_stressed}
    ])
    print("Performance Metrics:\n", metrics_df)
    metrics_df.to_csv(os.path.join('src', 'data', 'metrics.csv'), index=False)
    print("Metrics saved at:", os.path.join('src', 'data', 'metrics.csv'))

    plots_dir = os.path.join('src', 'data', 'plots')
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # Create P&L curve visualizations
    print("Generating plots...")
    if len(trades_df) > 0 and 'cumulative_pnl' in trades_df.columns:
        df1 = trades_df.to_pandas()
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df1 = df1.sort_values('timestamp')
        plt.figure(figsize=(12, 5))
        plt.plot(df1['timestamp'], df1['cumulative_pnl'], 'b-', linewidth=2)
        plt.title('Original Backtest: Cumulative P&L')
        plt.ylabel('P&L ($)')
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'unstressed_pnl.png'))
        plt.close()

    if len(stressed_trades_df) > 0 and 'cumulative_pnl' in stressed_trades_df.columns:
        df2 = stressed_trades_df.to_pandas()
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        df2 = df2.sort_values('timestamp')
        plt.figure(figsize=(12, 5))
        plt.plot(df2['timestamp'], df2['cumulative_pnl'], 'r-', linewidth=2)
        plt.title('Stressed Backtest (-5% Shock): Cumulative P&L')
        plt.ylabel('P&L ($)')
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'stressed_pnl.png'))
        plt.close()

    # Plot a comparison of drawdowns
    if len(trades_df) > 0 and 'cumulative_pnl' in trades_df.columns:
        orig_dd = calculate_drawdowns(trades_df.to_pandas())
        plt.figure(figsize=(12, 5))
        plt.plot(orig_dd['timestamp'], orig_dd['drawdown'], 'b-', label='Original')
        plt.title('Drawdown - Original')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(plots_dir, 'unstressed_drawdown.png'))
        plt.close()

    if len(stressed_trades_df) > 0 and 'cumulative_pnl' in stressed_trades_df.columns:
        stress_dd = calculate_drawdowns(stressed_trades_df.to_pandas())
        plt.figure(figsize=(12, 5))
        plt.plot(stress_dd['timestamp'], stress_dd['drawdown'], 'r-', label='Stressed (-5%)')
        plt.title('Drawdown - Stressed')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(plots_dir, 'stressed_drawdown.png'))
        plt.close()
    
    print("Plots saved in:", plots_dir)
    print("Backtesting and analysis complete.")

if __name__ == "__main__":
    main()