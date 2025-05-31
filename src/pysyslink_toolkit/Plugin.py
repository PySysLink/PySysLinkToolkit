import abc
import yaml

from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlockStructure

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

    @abc.abstractmethod
    def compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        pass

    @abc.abstractmethod
    def get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        pass

    def get_block_libraries(self):
        return self.block_libraries