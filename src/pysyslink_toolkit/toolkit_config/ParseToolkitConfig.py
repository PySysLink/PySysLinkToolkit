import yaml

from dacite import from_dict, Config
from pysyslink_toolkit.TextFileManager import load_yaml_file
from pysyslink_toolkit.toolkit_config.ToolkitConfig import ToolkitConfig


def parse_toolkit_config(toolkit_config_file: str) -> ToolkitConfig:
    data = load_yaml_file(toolkit_config_file)
    return from_dict(data_class=ToolkitConfig, data=data)