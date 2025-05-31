from typing import Any, Dict, List, Tuple

class LowLevelBlock:
    def __init__(self, id: str, name: str, block_type: str, block_class: str, **kwargs):
        self.id = id
        self.name = name
        self.block_type = block_type
        self.block_class = block_class
        self.extra = kwargs  # Any additional block-specific properties

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "Id": self.id,
            "Name": self.name,
            "BlockType": self.block_type,
            "BlockClass": self.block_class,
        }
        d.update(self.extra)
        return d

class LowLevelLink:
    def __init__(
        self,
        id: str,
        name: str,
        source_block_id: str,
        source_port_idx: int,
        destination_block_id: str,
        destination_port_idx: int,
    ):
        self.id = id
        self.name = name
        self.source_block_id = source_block_id
        self.source_port_idx = source_port_idx
        self.destination_block_id = destination_block_id
        self.destination_port_idx = destination_port_idx

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "SourceBlockId": self.source_block_id,
            "SourcePortIdx": self.source_port_idx,
            "DestinationBlockId": self.destination_block_id,
            "DestinationPortIdx": self.destination_port_idx,
        }

class LowLevelBlockStructure:
    def __init__(
        self,
        blocks: List[LowLevelBlock],
        links: List[LowLevelLink],
        port_map: Dict[Tuple[str, int], Tuple[str, int]],
    ):
        """
        port_map: maps (high_level_port_type, port_index) -> (low_level_block_id, low_level_port_index)
        Example: {("input", 0): ("sum1", 1), ("output", 0): ("display1", 0)}
        """
        self.blocks = blocks
        self.links = links
        self.port_map = port_map

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Blocks": [block.to_dict() for block in self.blocks],
            "Links": [link.to_dict() for link in self.links],
            "PortMap": {
                f"{ptype}_{pidx}": {"block_id": bid, "port_idx": lidx}
                for (ptype, pidx), (bid, lidx) in self.port_map.items()
            },
        }