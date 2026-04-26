

import abc
from typing import Optional

from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlockStructure
from pysyslink_toolkit.block_libraries.BlockLibraryPluginConfig import BlockLibraryPluginConfig, BlockTypeConfig


class BlockLibraryPlugin(abc.ABC):
    def __init__(self, block_library_plugin_config: BlockLibraryPluginConfig):
        self.block_library_plugin_config = block_library_plugin_config
        

    def get_block_type_config(self, block_library_name: str, block_type_name: str) -> Optional[BlockTypeConfig]:
        block_library = next(filter(lambda lib: lib.name == block_library_name, self.block_library_plugin_config.blockLibraries), None)
        if block_library == None:
            print(f"Block libraries available: {self.block_library_plugin_config.blockLibraries}")
            raise NotImplementedError(f"Block library {block_library_name} not in plugin {self.block_library_plugin_config.pluginName}")
        block_type = next(filter(lambda block_type: block_type.name == block_type_name, block_library.blockTypes))
        if block_type == None:
            raise NotImplementedError(f"Block type {block_type_name} not found on library {block_library.name} in plugin {self.block_library_plugin_config.pluginName}")
        return block_type

    def compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        return self._compile_block(high_level_block)

    @abc.abstractmethod
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        pass

    def get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        return self._get_block_render_information(high_level_block)

    def _get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        render_information = BlockRenderInformation()
        render_information.text = high_level_block.block_type
        
        block_type_config = self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        render_information.shape = block_type_config.blockShape

        # high_level_block.input_ports and .output_ports are originated from calls to this function, don't feedback

        configuration_values = {param_name: high_level_block.properties[param_name]["value"] for param_name in high_level_block.properties.keys()}
        print(f"configuration values for block: {configuration_values}")
        render_information.input_ports, render_information.output_ports = block_type_config.get_port_number(configuration_values)

        render_information.input_port_types, render_information.output_port_types = block_type_config.get_port_types(configuration_values)
        
        return render_information
    

    def get_block_html(self, high_level_block: HighLevelBlock, pslk_path: str) -> str:
        self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)
        html_or_none = self._get_block_html(high_level_block, pslk_path)
        if html_or_none == None:
            return f"No HTML for block {high_level_block.label} of type {high_level_block.block_library} {high_level_block.block_type}"
        else:
            return html_or_none

    def _get_block_html(self, high_level_block: HighLevelBlock, pslk_path: str) -> str | None:
        return None
