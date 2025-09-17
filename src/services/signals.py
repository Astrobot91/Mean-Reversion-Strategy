import polars as pl

def generate_signals(df):
	df = df.with_columns(
		pl.when(pl.col("close") < (pl.col("sma_20") - pl.col("std_dev_1")))
		  .then(1)
		  .when(pl.col("close") > (pl.col("sma_20") + pl.col("std_dev_1")))
		  .then(-1)
		  .otherwise(0)
		  .alias("signal")
	)
	df = df.with_columns(
		pl.col("signal").shift(1).over("symbol").alias("trade_entry_signal")
	).with_columns(
		pl.when(
			(pl.col("timestamp").dt.hour() == 15) & (pl.col("timestamp").dt.minute() == 30)
		).then(0).otherwise(pl.col("trade_entry_signal")).alias("trade_entry_signal")
	).fill_null(0)
	return df
