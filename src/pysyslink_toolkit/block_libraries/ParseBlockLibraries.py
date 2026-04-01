import importlib
import inspect
import pathlib
from typing import List
import os
import glob
import yaml

from dacite import from_dict, Config

from pysyslink_toolkit.TextFileManager import load_yaml_file
from pysyslink_toolkit.block_libraries.BlockLibraryPlugin import BlockLibraryPlugin
from pysyslink_toolkit.block_libraries.BlockLibraryPluginConfig import (
    BlockLibraryPluginConfig,
    BlockLibraryPluginType,
    BlockLibraryConfig,
    BlockTypeConfig,
    ConfigurationValue
)
from pysyslink_toolkit.BlockRenderInformation import BlockShape
from pysyslink_toolkit.block_libraries.CoreBlockLibraryPlugin import CoreBlockLibraryPlugin
from pysyslink_toolkit.toolkit_config.ParseToolkitConfig import parse_toolkit_config


def _normalize_block_type(block_type_dict: dict) -> dict:
    """Prepare block type dict so it matches BlockTypeConfig."""

    config_values = block_type_dict.get("configurationValues", [])
    config_dict = {}

    for cv in config_values:
        name = cv["name"]
        config_dict[name] = cv

    block_type_dict["configurationValues"] = config_dict

    # Extract render info
    render_info = block_type_dict.pop("renderInformation", None)
    if render_info and "blockShape" in render_info:
        block_type_dict["blockShape"] = render_info["blockShape"]

    return block_type_dict


def _normalize_plugin_dict(data: dict) -> dict:
    """Normalize YAML structure before dacite deserialization."""

    for library in data.get("blockLibraries", []):
        for i, block_type in enumerate(library.get("blockTypes", [])):
            library["blockTypes"][i] = _normalize_block_type(block_type)

    return data


def _parse_block_library_configs_from_paths(paths: List[str]) -> List[BlockLibraryPluginConfig]:

    plugin_configs: List[BlockLibraryPluginConfig] = []

    yaml_files: List[str] = []

    for path in paths:
        yaml_files.extend(
            glob.glob(os.path.join(path, "**", "*.pslkblp.yaml"), recursive=True)
        )
    
    dacite_config = Config(
        cast=[BlockLibraryPluginType, BlockShape]
    )

    for file_path in yaml_files:
        data = load_yaml_file(file_path)

        data = _normalize_plugin_dict(data)

        try:
            plugin = from_dict(
                data_class=BlockLibraryPluginConfig,
                data=data,
                config=dacite_config
            )
            plugin.yaml_filename = file_path
        except Exception as e:
            raise RuntimeError(f"Error wile loading plugin config from file: {file_path}. Error from dacite: {e}")

        plugin_configs.append(plugin)

    return plugin_configs


def load_block_library_plugins_from_paths(paths: List[str]) -> list[BlockLibraryPlugin]:
    plugin_configs = _parse_block_library_configs_from_paths(paths)
    
    plugins: list[BlockLibraryPlugin] = []
    
    for plugin_config in plugin_configs:
        if plugin_config.pluginType == BlockLibraryPluginType.HighLevelBlockLibrary:
            python_filename = plugin_config.metadata["pythonFilename"]
            py_path = pathlib.Path(plugin_config.yaml_filename).parent / python_filename
            module_name = py_path.stem # py_path.stem is correct, it returns the module name
            try: 
                plugins.append(load_high_level_plugin_from_file(py_path, module_name, plugin_config))
            except ImportError as e:
                print("Error loading plugin: {}".format(e.msg))
        elif plugin_config.pluginType == BlockLibraryPluginType.CoreBlockLibrary:
            plugins.append(CoreBlockLibraryPlugin(plugin_config))

            
    return plugins

def load_high_level_plugin_from_file(path: pathlib.Path, module_name: str, plugin_config: BlockLibraryPluginConfig) -> BlockLibraryPlugin:

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find a subclass of Plugin in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BlockLibraryPlugin) and obj is not BlockLibraryPlugin:
            return obj(plugin_config)  # Instantiate and return the plugin

    raise ImportError(f"No subclass of Plugin found in {path}")