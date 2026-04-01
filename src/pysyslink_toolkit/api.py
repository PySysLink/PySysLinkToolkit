import asyncio
import json
import os
import pathlib
import runpy
import traceback
import yaml
from typing import Any, Callable, Dict, List

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.HighLevelSystem import HighLevelSystem
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlockStructure
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.block_libraries.BlockLibraryPlugin import BlockLibraryPlugin
from pysyslink_toolkit.block_libraries.BlockLibraryPluginConfig import BlockLibraryConfig
from pysyslink_toolkit.block_libraries.ParseBlockLibraries import load_block_library_plugins_from_paths
from pysyslink_toolkit.compile_system import compile_pslk_to_yaml
from pysyslink_toolkit.simulate_system import simulate_system
from pysyslink_toolkit.TextFileManager import load_yaml_file
from pysyslink_toolkit.toolkit_config.ParseToolkitConfig import parse_toolkit_config

def compile_system(toolkit_config_path: str, pslk_path: str, output_yaml_path: str) -> str:
    """
    Compile a high-level system (dict) to a low-level system (dict).
    """

    try:
        compile_pslk_to_yaml(pslk_path, toolkit_config_path, output_yaml_path)
        return 'success'
    except Exception as e:
        print(f"Compilation failed: {e}")
        print(traceback.format_exc())
        return 'failure: {}'.format(traceback.format_exc())

async def run_simulation(toolkit_config_path: str | None, low_level_system: str, sim_options: str, 
                   display_callback: Callable = None) -> dict:
    """
    Run a simulation asynchronously (dummy implementation).
    """
    # This is a placeholder. You would implement your simulation logic here.
    # For now, just return a dummy result.

    toolkit_config = parse_toolkit_config(toolkit_config_path)
    plugin_paths = toolkit_config.get("base_block_type_support_plugin_paths", ["/usr/local/lib/pysyslink_plugins/block_type_supports"])
    result = await simulate_system(
        system_yaml_path=low_level_system,
        sim_options_yaml_path=sim_options,
        display_callback=display_callback,
        plugin_dir=plugin_paths
    )

    return result

def get_available_block_libraries(toolkit_config_path: str | None) -> List[BlockLibraryConfig]:
    """
    Return all available libraries and blocks from loaded plugins.
    """
    toolkit_config = parse_toolkit_config(toolkit_config_path)
    block_library_plugins = load_block_library_plugins_from_paths(toolkit_config.plugin_paths)
    libraries: list[BlockLibraryConfig] = []
    for plugin in block_library_plugins:
        libraries.extend(plugin.block_library_plugin_config.blockLibraries)
    return libraries

def get_block_render_information(toolkit_config_path: str | None, block_data: Dict[str, Any], pslk_path: str) -> BlockRenderInformation:
    """
    Return render information for a block.
    """
    toolkit_config = parse_toolkit_config(toolkit_config_path)
    block_library_plugins = load_block_library_plugins_from_paths(toolkit_config.plugin_paths)
    system_json = load_yaml_file(pslk_path)

    high_level_system, parameter_environment_dict = HighLevelSystem.from_dict(pslk_path, system_json)
    
    block = HighLevelBlock.from_dict(block_data, parameter_environment_dict)
    print(f"Block data for render: {block_data}")
    print(f"Looking for render info on block: {block.block_library}, {block.block_type}, {block.label}")
    for plugin in block_library_plugins:
        try:
            print(f"Testing plugin {plugin.block_library_plugin_config.pluginName}")
            return plugin.get_block_render_information(block)
        except NotImplementedError as e:
            print(f"Not implemented error happened: {e}")
            continue
        except Exception as e:
            raise RuntimeError(f"Exception while getting block render information: {e}")
    raise RuntimeError(f"No plugin could provide render information for block: {block.block_type}")

def get_block_html(toolkit_config_path: str | None, block_data: Dict[str, Any], pslk_path: str) -> str:
    block_library_plugins = load_block_library_plugins_from_paths(toolkit_config_path)

    system_json = load_yaml_file(pslk_path)

    high_level_system, parameter_environment_dict = HighLevelSystem.from_dict(pslk_path, system_json)
    
    block = HighLevelBlock.from_dict(block_data, parameter_environment_dict)    
    for plugin in block_library_plugins:
        try:
            return plugin.get_block_html(block, pslk_path)
        except NotImplementedError:
            continue
        except Exception as e:
            raise RuntimeError(f"Exception while getting block render information: {e}")
    raise RuntimeError(f"No plugin could provide render information for block: {block.block_type}")

if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "data")
    toolkit_config = os.path.join(test_dir, "toolkit_config.yaml")
    print(get_available_block_libraries(toolkit_config))