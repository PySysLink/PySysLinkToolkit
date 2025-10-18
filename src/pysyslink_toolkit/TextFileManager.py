import os
from typing import Any, Dict, List
import yaml

from pysyslink_toolkit import HighLevelSystem
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock




def _load_config(config_path: str | None) -> Dict[str, Any]:
    if config_path is None:
        return {}
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: '{config_path}'")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML parsing error in '{config_path}': {e}") from e
    except OSError as e:
        raise OSError(f"Could not open configuration file '{config_path}': {e}") from e
    
    if data is None:
        raise ValueError(f"Configuration file '{config_path}' is empty.")
    if not isinstance(data, dict):
        raise ValueError(
            f"Configuration file '{config_path}' must contain a YAML mapping (key-value pairs), "
            f"but got {type(data).__name__}."
        )
    return data

    