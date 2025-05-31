import asyncio
import pathlib
import yaml
from typing import Any, Callable, Dict, List

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlockStructure
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.load_plugins import load_plugins_from_paths
from pysyslink_toolkit.compile_system import compile_pslk_to_yaml
from pysyslink_toolkit.simulate_system import simulate_system

def _load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def compile_system(config_path: str, high_level_system_path: str, output_yaml_path: str) -> str:
    """
    Compile a high-level system (dict) to a low-level system (dict).
    """

    try:
        compile_pslk_to_yaml(high_level_system_path, config_path, output_yaml_path)
        return 'success'
    except Exception as e:
        return 'failure: {}'.format(e)

def run_simulation(config_path: str, low_level_system: str, sim_options: str, 
                   output_filename: str, 
                   display_callback: Callable[[str, float, float], None] = None) -> Any:
    """
    Run a simulation asynchronously (dummy implementation).
    """
    # This is a placeholder. You would implement your simulation logic here.
    # For now, just return a dummy result.


    simulate_system(
        low_level_system,
        sim_options,
        output_filename,
        display_callback,
        "/usr/local/lib"
    )

def get_available_block_libraries(config_path: str) -> List[Dict[str, Any]]:
    """
    Return all available libraries and blocks from loaded plugins.
    """
    config = _load_config(config_path)
    plugins = load_plugins_from_paths(config['plugin_paths'])
    libraries = []
    for plugin in plugins:
        if hasattr(plugin, "get_block_libraries"):
            libraries.extend(plugin.get_block_libraries())
    return libraries

def get_block_render_information(config_path: str, block_data: Dict[str, Any]) -> BlockRenderInformation:
    """
    Return render information for a block.
    """
    config = _load_config(config_path)
    plugins = load_plugins_from_paths(config['plugin_paths'])
    block = HighLevelBlock.from_dict(block_data)
    for plugin in plugins:
        try:
            return plugin.get_block_render_information(block)
        except NotImplementedError:
            continue
    raise RuntimeError(f"No plugin could provide render information for block: {block.block_type}")