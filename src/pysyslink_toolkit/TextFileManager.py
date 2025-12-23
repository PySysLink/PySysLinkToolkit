import os
from typing import Any, Dict, List
import yaml

from pysyslink_toolkit import HighLevelSystem
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock


def _resolve_single_path(p: str, config_dir: str) -> str:
    if p is None:
        return p
    p = str(p)
    if os.path.isabs(p):
        return p
    return os.path.abspath(os.path.join(config_dir, p))


def _resolve_path_value(value: Any, config_dir: str) -> Any:
    if isinstance(value, str):
        return _resolve_single_path(value, config_dir)
    if isinstance(value, list):
        return [(_resolve_single_path(v, config_dir) if isinstance(v, str) else v) for v in value]
    return value


def _load_toolkit_config(config_path: str | None) -> Dict[str, Any]:
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

    config_dir = os.path.dirname(os.path.abspath(config_path))
    return _resolve_paths_recursive(data, config_dir)


def _resolve_paths_recursive(obj: Any, config_dir: str) -> Any:
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if value is None:
                result[key] = value
                continue

            if "path" in key.lower() and isinstance(value, (str, list)):
                result[key] = _resolve_path_value(value, config_dir)
            else:
                result[key] = _resolve_paths_recursive(value, config_dir)
        return result

    if isinstance(obj, list):
        return [_resolve_paths_recursive(item, config_dir) for item in obj]

    return obj

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

    