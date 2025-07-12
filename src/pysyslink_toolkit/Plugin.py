import abc
from typing import Any, Dict
import yaml

import pysyslink_base

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation, BlockShape
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure


from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class ConfigurationValue:
    name: str
    defaultValue: Union[float, int, str, List[float], List[int], None]
    type: str
    metadata: dict = field(default_factory=dict)

@dataclass
class BlockTypeConfig:
    name: str
    configurationValues: Dict[str, ConfigurationValue] = field(default_factory=dict)
    blockShape: BlockShape = BlockShape.square
    metadata: dict = field(default_factory=dict)

@dataclass
class BlockLibraryConfig:
    name: str
    blockTypes: List[BlockTypeConfig] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclass
class PluginConfig:
    pluginName: str
    pluginType: str
    blockType: str
    blockLibraries: List[BlockLibraryConfig] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

def dict_to_plugin_config(data: dict) -> PluginConfig:
    def parse_configuration_value(cv):
        known = {k: cv[k] for k in ['name', 'defaultValue', 'type'] if k in cv}
        metadata = {k: v for k, v in cv.items() if k not in known}
        return ConfigurationValue(**known, metadata=metadata)

    def parse_block_type(bt):
        known = {k: bt[k] for k in ['name', 'configurationValues', 'blockShape'] if k in bt}
        metadata = {k: v for k, v in bt.items() if k not in known}
        # Convert list of config values to dict by name
        config_values = {
            cv["name"]: parse_configuration_value(cv)
            for cv in bt.get("configurationValues", [])
        }
        return BlockTypeConfig(
            name=bt["name"],
            configurationValues=config_values,
            blockShape=BlockShape(bt.get("blockShape")) if "blockShape" in bt else BlockShape.square,
            metadata=metadata
        )

    def parse_block_library(bl):
        known = {k: bl[k] for k in ['name', 'blockTypes'] if k in bl}
        metadata = {k: v for k, v in bl.items() if k not in known}
        return BlockLibraryConfig(
            name=bl["name"],
            blockTypes=[parse_block_type(bt) for bt in bl.get("blockTypes", [])],
            metadata=metadata
        )

    known = {k: data[k] for k in ['pluginName', 'pluginType', 'blockType', 'blockLibraries'] if k in data}
    metadata = {k: v for k, v in data.items() if k not in known}
    return PluginConfig(
        pluginName=data.get("pluginName"),
        pluginType=data.get("pluginType"),
        blockType=data.get("blockType"),
        blockLibraries=[parse_block_library(bl) for bl in data.get("blockLibraries", [])],
        metadata=metadata
    )


class Plugin(abc.ABC):
    def __init__(self, plugin_yaml: dict, toolkit_config: dict):
        super().__init__()
        if isinstance(plugin_yaml, str):
            plugin_yaml = yaml.safe_load(plugin_yaml)
        elif isinstance(plugin_yaml, dict):
            pass
        else:
            raise ValueError("plugin_yaml must be a dict or YAML string")
        self.config = dict_to_plugin_config(plugin_yaml)
        self.name = self.config.pluginName
        self.plugin_type = self.config.pluginType
        self.block_libraries = self.config.blockLibraries
        self.toolkit_config = toolkit_config

    
    def get_block_type_config(self, block_library_name: str, block_type_name: str) -> Optional[BlockTypeConfig]:
        block_library = next(filter(lambda lib: lib.name == block_library_name, self.block_libraries), None)
        if block_library == None:
            raise NotImplementedError(f"Block library {block_library_name} not in plugin {self.name}")
        block_type = next(filter(lambda block_type: block_type.name == block_type_name, block_library.blockTypes))
        if block_type == None:
            raise NotImplementedError(f"Block type {block_type_name} not found on library {block_library.name} in plugin {self.name}")
        return block_type

    def compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        block_type = self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        return self._compile_block(high_level_block)

    @abc.abstractmethod
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        pass

    def get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        block_type = self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        print(f"Block type {block_type} obtained for high level block {high_level_block.block_library}, {high_level_block.block_type}")
        return self._get_block_render_information(high_level_block)

    @abc.abstractmethod
    def _get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        pass
    
    def get_block_html(self, high_level_block: HighLevelBlock, pslk_path: str) -> str:
        block_type = self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        html_or_none = self._get_block_html(high_level_block, pslk_path)
        if html_or_none == None:
            return f"No HTML for block {high_level_block.label} of type {high_level_block.block_library} {high_level_block.block_type}"
        else:
            return html_or_none

    def _get_block_html(self, high_level_block: HighLevelBlock, pslk_path: str) -> str | None:
        return None

    def get_block_libraries(self):
        return self.block_libraries
    

    

