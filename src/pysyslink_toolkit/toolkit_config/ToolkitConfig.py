from dataclasses import dataclass
from typing import List


@dataclass
class ToolkitConfig:
    plugin_paths: List[str]
