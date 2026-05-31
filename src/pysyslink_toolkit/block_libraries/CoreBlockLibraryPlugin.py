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

        parameter_types = block_type.get_parameter_types({param_name: prop["value"] for param_name, prop in properties.items()})

        print(f"block_type: {block_type}")
        print(f"parameter_types: {parameter_types}")

        converted = {}
        for key, prop in properties.items():
            parameter_type = parameter_types.get(key)
            value = prop["value"]
            if parameter_type is None:
                raise ValueError(f"Property {key} not defined in block type {block_type_name} of library {block_library_name}")
            
            # Convert based on expected_type
            print(f"Converting property {key} with value {value} to expected type {parameter_type}")
            try:
                if parameter_type == "double":
                    converted[key + "[double]"] = float(value)
                elif parameter_type == "int":
                    converted[key + "[int]"] = int(value)
                elif parameter_type == "bool":
                    converted[key + "[bool]"] = bool(value)
                elif parameter_type == "string":
                    converted[key + "[string]"] = str(value)
                elif parameter_type == "complex_double":
                    converted[key + "[complex_double]"] = complex(value)
                elif parameter_type.endswith("[]") and isinstance(value, list):
                    base_type = parameter_type[:-2]
                    if base_type == "double":
                        converted[key + "[vector<double>]"] = [float(v) for v in value]
                    elif base_type == "int":
                        converted[key + "[vector<int>]"] = [int(v) for v in value]
                    elif base_type == "string":
                        converted[key + "[vector<string>]"] = [str(v) for v in value]
                    elif base_type == "complex_double":
                        converted[key + "[vector<complex_double>]"] = [complex(v) for v in value]
                    else:
                        converted[key + "[vector<string>]"] = [str(v) for v in value]
                else:
                    converted[key + "[string]"] = value
            except Exception as e:
                raise ValueError(f"Error converting type of property {key} to type {parameter_type}, value {value}: {e}")
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
            input_port_types=[input_port_type.to_string() for input_port_type in high_level_block.input_port_types],
            output_port_number=high_level_block.output_ports,
            output_port_types=[output_port_type.to_string() for output_port_type in high_level_block.output_port_types],
            **converted_properties
        )
        # Map input and output ports directly
        port_map = {}
        for i in range(high_level_block.input_ports):
            port_map[("input", i)] = (low_level_block.id, i)
        for i in range(high_level_block.output_ports):
            port_map[("output", i)] = (low_level_block.id, i)
        return LowLevelBlockStructure([low_level_block], [], port_map)



    