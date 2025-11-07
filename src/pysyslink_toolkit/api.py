import asyncio
import json
import os
import pathlib
import runpy
import traceback
import pysyslink_base
import yaml
from typing import Any, Callable, Dict, List

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.HighLevelSystem import HighLevelSystem
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlockStructure
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.Plugin import BlockLibraryConfig
from pysyslink_toolkit.load_plugins import load_plugins_from_paths
from pysyslink_toolkit.compile_system import compile_pslk_to_yaml
from pysyslink_toolkit.simulate_system import simulate_system
from pysyslink_toolkit.TextFileManager import _load_config

def compile_system(config_path: str | None, pslk_path: str, output_yaml_path: str) -> str:
    """
    Compile a high-level system (dict) to a low-level system (dict).
    """

    try:
        compile_pslk_to_yaml(pslk_path, config_path, output_yaml_path)
        return 'success'
    except Exception as e:
        print(f"Compilation failed: {e}")
        print(traceback.format_exc())
        return 'failure: {}'.format(traceback.format_exc())

async def run_simulation(config_path: str | None, low_level_system: str, sim_options: str, 
                   display_callback: Callable[[pysyslink_base.ValueUpdateBlockEvent], None] = None) -> dict:
    """
    Run a simulation asynchronously (dummy implementation).
    """
    # This is a placeholder. You would implement your simulation logic here.
    # For now, just return a dummy result.

    config = _load_config(config_path)
    plugin_paths = config.get("base_block_type_support_plugin_paths", ["/usr/local/lib/pysyslink_plugins/block_type_supports"])
    plugin_configuration = config.get("base_plugin_configuration", {"BasicCppSupport/libraryPluginPath": "/usr/local/lib/pysyslink_plugins"})
    result = await simulate_system(
        low_level_system,
        sim_options,
        display_callback,
        plugin_paths,
        plugin_configuration
    )

    return result

def get_available_block_libraries(config_path: str | None) -> List[BlockLibraryConfig]:
    """
    Return all available libraries and blocks from loaded plugins.
    """
    plugins = load_plugins_from_paths(config_path)
    libraries: list[BlockLibraryConfig] = []
    for plugin in plugins:
        if hasattr(plugin, "get_block_libraries"):
            libraries.extend(plugin.get_block_libraries())
    return libraries

def get_block_render_information(config_path: str | None, block_data: Dict[str, Any], pslk_path: str) -> BlockRenderInformation:
    """
    Return render information for a block.
    """
    plugins = load_plugins_from_paths(config_path)

    system_json = _load_config(pslk_path)

    high_level_system, parameter_environment_dict = HighLevelSystem.from_dict(pslk_path, system_json)
    
    block = HighLevelBlock.from_dict(block_data, parameter_environment_dict)
    for plugin in plugins:
        try:
            print(f"Testing plugin {plugin.name}")
            return plugin.get_block_render_information(block)
        except NotImplementedError:
            continue
        except Exception as e:
            raise RuntimeError(f"Exception while getting block render information: {e}")
    raise RuntimeError(f"No plugin could provide render information for block: {block.block_type}")

def get_block_html(config_path: str | None, block_data: Dict[str, Any], pslk_path: str) -> str:
    plugins = load_plugins_from_paths(config_path)

    system_json = _load_config(pslk_path)

    high_level_system, parameter_environment_dict = HighLevelSystem.from_dict(pslk_path, system_json)
    
    block = HighLevelBlock.from_dict(block_data, parameter_environment_dict)    
    for plugin in plugins:
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