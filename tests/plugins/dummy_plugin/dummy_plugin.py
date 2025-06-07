from pysyslink_toolkit.Plugin import Plugin
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelLink, LowLevelBlockStructure
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation

class DummyPlugin(Plugin):
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        # Always returns a dummy block structure
        if high_level_block.block_library != "dummy_library" or high_level_block.block_type != "dummy":
            raise NotImplementedError("Only dummy blocks are handled by this plugin.")
        
        block = LowLevelBlock(
            id="dummy", name="Dummy", block_type="DummyType", block_class="DummyClass"
        )
        return LowLevelBlockStructure([block], [], {("output", 0): ("dummy", 0)})

    def _get_block_render_information(self, high_level_block: HighLevelBlock) -> BlockRenderInformation:
        return BlockRenderInformation()