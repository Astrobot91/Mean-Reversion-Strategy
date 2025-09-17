import os
import polars as pl

LOOKBACK_INTERVAL = 20

def load_and_resample_data(csv_path):
	sample_data = pl.read_csv(csv_path)
	sample_data = sample_data.with_columns(
		(pl.col('timestamp').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")),
	).with_columns(
		(pl.col("timestamp").dt.truncate("1m").alias("timestamp"))
	).group_by(
		["timestamp", "symbol"]
		).agg([
				pl.first("price").alias("open"),
				pl.max("price").alias("high"),
				pl.min("price").alias("low"),
				pl.last("price").alias("close"),
				pl.sum("volume").alias("volume")
		]).sort(['symbol', 'timestamp'])
	sample_data = sample_data.with_columns([
		pl.col("close").rolling_mean(window_size=LOOKBACK_INTERVAL).over("symbol").alias("sma_20"),
		pl.col("close").rolling_std(window_size=LOOKBACK_INTERVAL).over("symbol").alias("std_dev_1"),
	])
	return sample_data

def save_parquet(data, out_path):
	data.write_parquet(out_path)
