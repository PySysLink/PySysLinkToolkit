from typing import Any, Dict

import pysyslink_base
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure
from pysyslink_toolkit.Plugin import Plugin


class CoreBlockPlugin(Plugin):
    def __init__(self, plugin_yaml, toolkit_config: dict):
        super().__init__(plugin_yaml, toolkit_config)
        for block_library in self.block_libraries:
            block_library.name = "core_" + block_library.name
        print(self.config.metadata)
        self.block_type = self.config.blockType
    
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
            block_type=self.block_type,
            block_class=self._get_block_class(high_level_block.block_library, high_level_block.block_type),
            **converted_properties
        )
        # Map input and output ports directly
        port_map = {}
        for i in range(high_level_block.input_ports):
            port_map[("input", i)] = (low_level_block.id, i)
        for i in range(high_level_block.output_ports):
            port_map[("output", i)] = (low_level_block.id, i)
        return LowLevelBlockStructure([low_level_block], [], port_map)

    def _get_block_render_information(self, high_level_block) -> BlockRenderInformation:
        render_information = BlockRenderInformation()
        render_information.text = high_level_block.block_type
        
        print("type config: {}".format(self.get_block_type_config(high_level_block.block_library, high_level_block.block_type)))
        render_information.shape = self.get_block_type_config(high_level_block.block_library, high_level_block.block_type).blockShape

        # --- Convert high-level block to low-level block first ---
        low_level_struct = self._compile_block(high_level_block)
        if not low_level_struct.blocks:
            raise ValueError("No low-level blocks generated from high-level block.")

        low_level_block = low_level_struct.blocks[0]
        block_configuration = low_level_block.to_dict()

        # --- Add/override required fields for base block instantiation ---
        block_configuration["BlockType"] = self.block_type
        block_configuration["BlockClass"] = self._get_block_class(high_level_block.block_library, high_level_block.block_type)
        block_configuration["Name"] = low_level_block.name
        block_configuration["Id"] = low_level_block.id

        base_block = self.get_base_block(block_configuration)
        render_information.input_ports = len(base_block.get_input_ports())
        render_information.output_ports = len(base_block.get_output_ports())
        return render_information

    
    def get_base_block(self, block_configuration: dict[str, Any]):
        try:
            pysyslink_base.SpdlogManager.configure_default_logger()
        except:
            pass
        
        pysyslink_base.SpdlogManager.set_log_level(pysyslink_base.LogLevel.off)

        plugin_dir = self.toolkit_config.get("base_block_type_support_plugin_paths", ["/usr/local/lib/pysyslink_plugins/block_type_supports"])
        plugin_configuration = self.toolkit_config.get("base_plugin_configuration", {"BasicCppSupport/libraryPluginPath": "/usr/local/lib/pysyslink_plugins"})

        plugin_loader = pysyslink_base.BlockTypeSupportPluginLoader()

        if isinstance(plugin_dir, str):
            plugin_dir = [plugin_dir]
        
        for dir in plugin_dir:
            block_factories = plugin_loader.load_plugins(dir, plugin_configuration)

        block_events_handler = pysyslink_base.BlockEventsHandler()

        print("Block factories: {}".format(block_factories))
        block_factory = block_factories.get(self.block_type, None)
        if block_factory != None:
            try:
                return block_factory.create_block(block_configuration, block_events_handler)
            except Exception as e:
                raise ValueError("Could not create a block of type {}. Exception: {}".format(self.block_type, e))
        else:
            raise ValueError("Block type: {} not found on block factories loaded as plugins on base.".format(self.block_type))
        
