import polars as pl
from dataclasses import dataclass


@dataclass
class BacktestParams:
	commission_rate: float = 1     # 1 bps
	max_positions: int = 1000
	starting_capital: float = 1000000
	max_daily_loss: float = 0.02
	qty_per_position: int = 500
	shock_percentage: float = 0.05
	window_size: int = 20

	@classmethod
	def from_dict(cls, d):
		return cls(**d)

def run_backtest(backtest_data, params: BacktestParams):
	import duckdb
	conn = duckdb.connect()
	conn.register("backtest_data", backtest_data)
	timestamps = backtest_data.select(pl.col("timestamp").unique().sort()).to_series().to_list()
	positions = {}
	trades = []
	daily_pnl = 0
	max_daily_loss = params.max_daily_loss * params.starting_capital
	for timestamp in timestamps:
		current_data = conn.execute(f"""
			SELECT * FROM backtest_data
			WHERE timestamp = '{timestamp}'
		""").df()
		if daily_pnl <= -max_daily_loss:
			break
		if current_data["trade_entry_signal"].sum() == 0:
			continue
		current_data = pl.from_pandas(current_data)
		for row in current_data.iter_rows(named=True):
			symbol = row['symbol']
			price = row['close']
			signal = row['signal']
			trade_entry_signal = row['trade_entry_signal']
			if symbol not in positions:
				positions[symbol] = 0
			commission = 0
			qty_traded = 0
			trade_pnl = 0
			if trade_entry_signal == 1 and positions[symbol] >= 0:
				if positions[symbol] + params.qty_per_position <= params.max_positions:
					qty_traded = params.qty_per_position
					positions[symbol] += qty_traded
					commission = qty_traded * price * params.commission_rate / 10000
				trades.append({
					'timestamp': timestamp,
					'symbol': symbol,
					'price': price,
					'quantity': qty_traded,
					'direction': 'BUY',
					'position': positions[symbol],
					'commission': commission
				})
			if trade_entry_signal == -1 and positions[symbol] <= 0:
				if abs(positions[symbol] - params.qty_per_position) <= params.max_positions:
					qty_traded = params.qty_per_position
					positions[symbol] -= qty_traded
					commission = qty_traded * price * params.commission_rate / 10000
				trades.append({
					'timestamp': timestamp,
					'symbol': symbol,
					'price': price,
					'quantity': qty_traded,
					'direction': 'SELL',
					'position': positions[symbol],
					'commission': commission
				})
			if positions[symbol] > 0 and signal == -1:
				qty_traded = positions[symbol]
				exit_price = price
				commission = qty_traded * price * params.commission_rate / 10000
				prev_trades = [t for t in trades if t['symbol'] == symbol and t['direction'] == 'BUY']
				avg_entry_price = sum([t['price'] * t['quantity'] for t in prev_trades]) / sum([t['quantity'] for t in prev_trades])
				trade_pnl = (exit_price - avg_entry_price) * qty_traded - commission
				daily_pnl += trade_pnl
				trades.append({
					'timestamp': timestamp,
					'symbol': symbol,
					'price': exit_price,
					'quantity': qty_traded,
					'direction': 'SELL',
					'position': 0,
					'commission': commission,
					'pnl': trade_pnl
				})
				positions[symbol] = 0
			elif positions[symbol] < 0 and signal == 1:
				qty_traded = abs(positions[symbol])
				exit_price = price
				commission = qty_traded * price * params.commission_rate / 10000
				prev_trades = [t for t in trades if t['symbol'] == symbol and t['direction'] == 'SELL']
				avg_entry_price = sum([t['price'] * t['quantity'] for t in prev_trades]) / sum([t['quantity'] for t in prev_trades])
				trade_pnl = (avg_entry_price - exit_price) * qty_traded - commission
				daily_pnl += trade_pnl
				trades.append({
					'timestamp': timestamp,
					'symbol': symbol,
					'price': exit_price,
					'quantity': qty_traded,
					'direction': 'BUY',
					'position': 0,
					'commission': commission,
					'pnl': trade_pnl
				})
				positions[symbol] = 0
	trades_df = pl.DataFrame(trades)
	if len(trades_df) > 0 and 'pnl' in trades_df.columns:
		trades_df = trades_df.with_columns(pl.col('pnl').fill_null(0))
		trades_df = trades_df.with_columns(pl.col('pnl').cum_sum().alias('cumulative_pnl'))
	return trades_df
