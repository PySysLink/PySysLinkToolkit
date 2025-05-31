from typing import Any, Dict

class HighLevelBlock:
    def __init__(
        self,
        id: str,
        label: str,
        input_ports: int,
        output_ports: int,
        block_library: str,
        block_type: str,
        properties: Dict[str, Any]
    ):
        self.id = id
        self.label = label
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.block_library = block_library
        self.block_type = block_type
        self.properties = properties

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HighLevelBlock":
        return cls(
            id=data["id"],
            label=data["label"],
            input_ports=data.get("inputPorts", 0),
            output_ports=data.get("outputPorts", 0),
            block_library=data.get("block_library", 0),
            block_type=data.get("block_type", 0),
            properties=data.get("properties", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "inputPorts": self.input_ports,
            "outputPorts": self.output_ports,
            "block_library": self.block_library,
            "block_type": self.block_type,
            "properties": self.properties,
        }