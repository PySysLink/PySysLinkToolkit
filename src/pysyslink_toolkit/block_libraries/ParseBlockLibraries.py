from ast import Dict
from copy import deepcopy
import importlib
import inspect
import pathlib
from typing import Any, List
import os
import glob
import yaml

from dacite import from_dict, Config

from pysyslink_toolkit.PortType import PortType
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

    for i, common_block_type in enumerate(data.get("commonBlocks", [])):
        data["commonBlocks"][i] = _normalize_block_type(common_block_type)

    for library in data.get("blockLibraries", []):
        for i, block_type in enumerate(library.get("blockTypes", [])):
            library["blockTypes"][i] = _normalize_block_type(block_type)

    return data


def _solve_block_library_config_common_blocks(plugin: BlockLibraryPluginConfig) -> BlockLibraryPluginConfig:
    """
    Resolve `commonBlocks` inheritance.

    A block type may declare:
        commonBlock: "<name>"

    Then the referenced common block acts as a base definition.

    Rules:
    - Child values override parent values
    - configurationValues are merged by key
    - metadata is merged (child overrides parent keys)
    - Missing scalar properties are inherited
    - Port type dictionaries are merged (child overrides same keys)
    """

    # ---------------------------------------------------------
    # Build lookup of common blocks by name
    # ---------------------------------------------------------
    common_map: dict[str, BlockTypeConfig] = {}

    for common in plugin.commonBlocks:
        common_map[common.name] = common

    # ---------------------------------------------------------
    # Resolve all libraries
    # ---------------------------------------------------------
    solved_libraries: list[BlockLibraryConfig] = []

    for library in plugin.blockLibraries:
        solved_blocks: list[BlockTypeConfig] = []

        for block in library.blockTypes:
            solved_blocks.append(
                _solve_single_block_with_common(block, common_map)
            )

        solved_libraries.append(
            BlockLibraryConfig(
                name=library.name,
                blockTypes=solved_blocks,
                metadata=deepcopy(library.metadata),
            )
        )

    return BlockLibraryPluginConfig(
        pluginName=plugin.pluginName,
        pluginType=plugin.pluginType,
        blockType=plugin.blockType,
        yaml_filename=plugin.yaml_filename,
        commonBlocks=deepcopy(plugin.commonBlocks),
        blockLibraries=solved_libraries,
        metadata=deepcopy(plugin.metadata),
    )


def _solve_single_block_with_common(block: BlockTypeConfig, common_map: dict[str, BlockTypeConfig]) -> BlockTypeConfig:
    """
    Resolve one block against its commonBlock base.
    """

    common_name = block.commonBlock

    if not common_name:
        return deepcopy(block)

    if common_name not in common_map:
        raise ValueError(
            f"Block '{block.name}' references unknown commonBlock "
            f"'{common_name}'"
        )

    base = common_map[common_name]

    # ---------------------------------------------------------
    # Merge configuration values
    # ---------------------------------------------------------
    merged_config = deepcopy(base.configurationValues)
    merged_config.update(deepcopy(block.configurationValues))

    # ---------------------------------------------------------
    # Merge metadata
    # ---------------------------------------------------------
    merged_metadata = deepcopy(base.metadata)
    merged_metadata.update(deepcopy(block.metadata))

    # ---------------------------------------------------------
    # Merge port type definitions
    # ---------------------------------------------------------
    merged_input_types = deepcopy(base.inputPortTypes)
    merged_input_types.update(deepcopy(block.inputPortTypes))

    merged_output_types = deepcopy(base.outputPortTypes)
    merged_output_types.update(deepcopy(block.outputPortTypes))

    # ---------------------------------------------------------
    # Child overrides parent when explicitly set
    # ---------------------------------------------------------
    solved = BlockTypeConfig(
        name=block.name,

        inputPortNumber=block.inputPortNumber,

        outputPortNumber=block.outputPortNumber,

        inputPortTypes=merged_input_types,
        outputPortTypes=merged_output_types,

        configurationValues=merged_config,

        blockShape=(
            block.blockShape
            if block.blockShape is not None
            else base.blockShape
        ),

        metadata=merged_metadata,
    )

    return solved

def _parse_block_library_configs_from_paths(paths: List[str]) -> List[BlockLibraryPluginConfig]:

    plugin_configs: List[BlockLibraryPluginConfig] = []

    yaml_files: List[str] = []

    for path in paths:
        print("GLOBBING PATH:", path, flush=True)
        yaml_files.extend(
            glob.glob(os.path.join(path, "**", "*.pslkblp.yaml"), recursive=True)
        )
    
    dacite_config = Config(
        cast=[BlockLibraryPluginType, BlockShape],
        type_hooks={
            PortType: PortType.from_dict
        }
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
        
        solved_plugin = _solve_block_library_config_common_blocks(plugin)

        plugin_configs.append(solved_plugin)

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

def resolve_block_libraries(libraries: List[BlockLibraryConfig]) -> List[BlockLibraryConfig]:
    """
    Resolve block libraries, by calculating the default port numbers based on the default config values.
    This is needed for block rendering during instantiation, the frontend don't know to resolve port numbers.
    """
    resolved_libraries: List[BlockLibraryConfig] = []

    for lib in libraries:
        resolved_block_types: List[BlockTypeConfig] = []

        for block in lib.blockTypes:
            # 1. Build configuration values dict
            config_values: Dict[str, Any] = {}

            for name, cfg in block.configurationValues.items():
                if cfg.defaultValue is not None:
                    config_values[name] = cfg.defaultValue
                else:
                    # Fallbacks based on type
                    if cfg.type.endswith("[]"):
                        config_values[name] = [1]
                    elif cfg.type in ("int", "float"):
                        config_values[name] = 1
                    else:
                        config_values[name] = 1  # safe fallback

            # 2. Resolve ports
            try:
                input_ports, output_ports = block.get_port_number(config_values)
            except Exception as e:
                raise ValueError(
                    f"Error resolving block '{block.name}' in library '{lib.name}': {e}"
                )

            # 3. Create resolved copy
            resolved_block = BlockTypeConfig(
                name=block.name,
                inputPortNumber=input_ports,
                outputPortNumber=output_ports,
                configurationValues=block.configurationValues,
                blockShape=block.blockShape,
                metadata=block.metadata.copy(),
            )

            resolved_block_types.append(resolved_block)

        resolved_lib = BlockLibraryConfig(
            name=lib.name,
            blockTypes=resolved_block_types,
            metadata=lib.metadata.copy(),
        )

        resolved_libraries.append(resolved_lib)

    return resolved_libraries

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