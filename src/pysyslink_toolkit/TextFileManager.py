from typing import Any, Dict, List
import yaml

from pysyslink_toolkit import HighLevelSystem
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock




def _load_config(config_path: str | None) -> Dict[str, Any]:
    if config_path is None:
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
    