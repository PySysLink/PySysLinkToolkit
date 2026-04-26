from typing import Any, Dict

from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure
from pysyslink_toolkit.block_libraries.BlockLibraryPlugin import BlockLibraryPlugin
from pysyslink_toolkit.block_libraries.BlockLibraryPluginConfig import BlockLibraryPluginConfig


class CoreBlockLibraryPlugin(BlockLibraryPlugin):
    def __init__(self, block_library_plugin_config: BlockLibraryPluginConfig):
        super().__init__(block_library_plugin_config)
        for block_library in self.block_library_plugin_config.blockLibraries:
            block_library.name = "core_" + block_library.name
    
    def _convert_property_types(self, block_library_name: str, block_type_name: str, properties: Dict[str, Dict[str, Any]]):
        # Find the block library and block type definition
        block_type = self.get_block_type_config(block_library_name, block_type_name)

        converted = {}
        for key, prop in properties.items():
            prop_configuration = block_type.configurationValues.get(key)
            value = prop["value"]
            if prop_configuration is None:
                converted[key] = value  # or raise error if you want strictness
                continue
            # Convert based on expected_type
            expected_type = prop_configuration.type
            try:
                if expected_type == "float":
                    converted[key] = float(value)
                elif expected_type == "int":
                    converted[key] = int(value)
                elif expected_type == "bool":
                    converted[key] = bool(value)
                elif expected_type == "string":
                    converted[key] = str(value)
                elif expected_type.endswith("[]") and isinstance(value, list):
                    base_type = expected_type[:-2]
                    if base_type == "float":
                        converted[key] = [float(v) for v in value]
                    elif base_type == "int":
                        converted[key] = [int(v) for v in value]
                    elif base_type == "string":
                        converted[key] = [str(v) for v in value]
                    else:
                        converted[key] = value
                else:
                    converted[key] = value
            except Exception as e:
                raise ValueError(f"Error converting type of property {key} to type {expected_type}, value {value}: {e}")
        return converted

    def _get_block_class(self, block_library, block_type) -> str:
        if block_library.startswith("core_"):
            block_library = block_library[5:]
        return block_library + "/" + block_type

    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        converted_properties = self._convert_property_types(
            high_level_block.block_library,
            high_level_block.block_type,
            high_level_block.properties
        )
        # Create a LowLevelBlock with the same attributes as the high-level block

        low_level_block = LowLevelBlock(
            id=high_level_block.id,
            name=high_level_block.label,
            block_type=self.block_library_plugin_config.blockType,
            block_class=self._get_block_class(high_level_block.block_library, high_level_block.block_type),
            input_port_number=high_level_block.input_ports,
            input_port_types=high_level_block.input_port_types,
            output_port_number=high_level_block.output_ports,
            output_port_types=high_level_block.output_port_types,
            **converted_properties
        )
        # Map input and output ports directly
        port_map = {}
        for i in range(high_level_block.input_ports):
            port_map[("input", i)] = (low_level_block.id, i)
        for i in range(high_level_block.output_ports):
            port_map[("output", i)] = (low_level_block.id, i)
        return LowLevelBlockStructure([low_level_block], [], port_map)



    