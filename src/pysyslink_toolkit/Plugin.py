import abc
import yaml

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure

class Plugin(abc.ABC):
    def __init__(self, plugin_yaml: dict):
        super().__init__()
        if isinstance(plugin_yaml, str):
            self.config = yaml.safe_load(plugin_yaml)
        elif isinstance(plugin_yaml, dict):
            self.config = plugin_yaml
        else:
            raise ValueError("plugin_yaml must be a dict or YAML string")
        self.name = self.config.get("pluginName", "UnnamedPlugin")
        self.plugin_type = self.config.get("pluginType", "")
        self.block_libraries = self.config.get("blockLibraries", [])

    def compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        return self._compile_block(high_level_block)

    @abc.abstractmethod
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        pass

    def get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        block_render_information = BlockRenderInformation()
        block_render_information.text = high_level_block.block_type

    def get_block_libraries(self):
        return self.block_libraries
    

class CoreBlockPlugin(Plugin):
    def __init__(self, plugin_yaml):
        super().__init__(plugin_yaml)
        for block_library in self.block_libraries:
            block_library["name"] = "core_" + block_library["name"]
        self.block_type = plugin_yaml["blockType"]

    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        # Create a LowLevelBlock with the same attributes as the high-level block
        block_library = high_level_block.block_library
        if block_library.startswith("core_"):
            block_library = block_library[5:]
        low_level_block = LowLevelBlock(
            id=high_level_block.id,
            name=high_level_block.label,
            block_type=self.block_type,
            block_class=block_library + "/" + high_level_block.block_type,
            **high_level_block.properties
        )
        # Map input and output ports directly
        port_map = {}
        for i in range(high_level_block.input_ports):
            port_map[("input", i)] = (low_level_block.id, i)
        for i in range(high_level_block.output_ports):
            port_map[("output", i)] = (low_level_block.id, i)
        return LowLevelBlockStructure([low_level_block], [], port_map)
