import numpy as np
import pandas as pd


def calculate_performance_metrics(trades_df: pd.DataFrame) -> dict:
	metrics = {}
	df = trades_df.to_pandas()
	df['timestamp'] = pd.to_datetime(df['timestamp'])
	completed_trades = df[df['pnl'].notnull()] if 'pnl' in df.columns else df
	metrics['total_trades'] = len(completed_trades)
	metrics['profitable_trades'] = len(completed_trades[completed_trades['pnl'] > 0])
	metrics['win_rate'] = metrics['profitable_trades'] / metrics['total_trades'] if metrics['total_trades'] > 0 else 0
	metrics['total_pnl'] = completed_trades['pnl'].sum() if 'pnl' in completed_trades.columns else 0
	metrics['avg_return'] = completed_trades['pnl'].mean() if 'pnl' in completed_trades.columns else 0
	metrics['max_return'] = completed_trades['pnl'].max() if 'pnl' in completed_trades.columns else 0
	metrics['min_return'] = completed_trades['pnl'].min() if 'pnl' in completed_trades.columns else 0
	avg_win = completed_trades.loc[completed_trades['pnl'] > 0, 'pnl'].mean() or 0 if 'pnl' in completed_trades.columns else 0
	avg_loss = abs(completed_trades.loc[completed_trades['pnl'] < 0, 'pnl'].mean() or 1) if 'pnl' in completed_trades.columns else 1
	metrics['avg_win_loss_ratio'] = avg_win / avg_loss if avg_loss != 0 else float('inf')
	if len(completed_trades) > 1 and 'pnl' in completed_trades.columns:
		minute_returns = completed_trades.groupby(completed_trades['timestamp'].dt.floor('min'))['pnl'].sum()
		if minute_returns.std() != 0:
			metrics['intraday_sharpe'] = (minute_returns.mean() / minute_returns.std()) * np.sqrt(minute_returns.count())
		else:
			metrics['intraday_sharpe'] = 0
	else:
		metrics['intraday_sharpe'] = 0
	if 'cumulative_pnl' in completed_trades.columns:
		cumulative = completed_trades.sort_values('timestamp')
		running_max = cumulative['cumulative_pnl'].cummax()
		drawdown = (cumulative['cumulative_pnl'] - running_max) / running_max if running_max.max() > 0 else 0
		metrics['max_drawdown'] = drawdown.min() if hasattr(drawdown, 'min') else 0
	else:
		metrics['max_drawdown'] = 0
	return metrics

def calculate_drawdowns(df: pd.DataFrame) -> pd.DataFrame:
	df = df.sort_values('timestamp')
	df['peak'] = df['cumulative_pnl'].cummax()
	df['drawdown'] = (df['cumulative_pnl'] - df['peak']) / df['peak'] * 100
	return df
