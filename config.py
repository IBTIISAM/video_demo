# config.py

import yaml
from pathlib import Path


def load_config(config_file="config.yaml"):
    config_path = Path(config_file)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file {config_file} not found.")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config


config = load_config()
