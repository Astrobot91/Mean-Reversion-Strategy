import yaml

# Loads the config file and returns the strategy parameters as a dict
def load_strategy_config(config_path, strategy_name):
	with open(config_path, 'r') as f:
		config = yaml.safe_load(f)
	return config[strategy_name]
