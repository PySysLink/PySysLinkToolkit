import pysyslink_toolkit
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelLink, LowLevelBlockStructure
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock

class NeuronPlugin(pysyslink_toolkit.Plugin):
    def get_block_render_information(self, high_level_block):
        return BlockRenderInformation()    
    
    def compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        # Only handle neuron blocks
        if high_level_block.block_library != "neuron_library" or high_level_block.block_type != "neuron":
            raise NotImplementedError("Only neuron blocks are handled by this plugin.")

        n = high_level_block.input_ports
        gains = high_level_block.properties.get("gains", [1.0] * (n - 1))
        offset = high_level_block.properties.get("offset", 0.0)

        blocks = []
        links = []
        port_map = {}

        # Create gain blocks for first n-1 inputs
        gain_block_ids = []
        for i in range(n - 1):
            gain_id = f"{high_level_block.id}_gain{i}"
            gain_block = LowLevelBlock(
                id=gain_id,
                name=f"Gain {i+1}",
                block_type="BasicCpp",
                block_class="BasicBlocks/Gain",
                Gain=gains[i] if i < len(gains) else 1.0
            )
            blocks.append(gain_block)
            gain_block_ids.append(gain_id)
            # Map high-level input port to gain block input
            port_map[("input", i)] = (gain_id, 0)

        # Offset block for last input
        offset_id = f"{high_level_block.id}_offset"
        offset_block = LowLevelBlock(
            id=offset_id,
            name="Offset",
            block_type="BasicCpp",
            block_class="BasicBlocks/Constant",
            Value=offset
        )
        blocks.append(offset_block)
        port_map[("input", n - 1)] = (offset_id, 0)

        # Adder block
        adder_id = f"{high_level_block.id}_adder"
        adder_block = LowLevelBlock(
            id=adder_id,
            name="Adder",
            block_type="BasicCpp",
            block_class="BasicBlocks/Adder",
            Gains=[1.0] * n  # All inputs summed
        )
        blocks.append(adder_block)

        # Connect gain blocks and offset to adder
        link_idx = 0
        for i, gain_id in enumerate(gain_block_ids):
            link = LowLevelLink(
                id=f"{high_level_block.id}_link{link_idx}",
                name=f"link_gain{i+1}_to_adder",
                source_block_id=gain_id,
                source_port_idx=0,
                destination_block_id=adder_id,
                destination_port_idx=i
            )
            links.append(link)
            link_idx += 1

        # Offset to adder
        link = LowLevelLink(
            id=f"{high_level_block.id}_link{link_idx}",
            name="link_offset_to_adder",
            source_block_id=offset_id,
            source_port_idx=0,
            destination_block_id=adder_id,
            destination_port_idx=n - 1
        )
        links.append(link)

        # Output port mapping: adder output 0
        port_map[("output", 0)] = (adder_id, 0)

        return LowLevelBlockStructure(blocks, links, port_map)