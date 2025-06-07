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
        properties: Dict[str, Dict[str, Any]]
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
        required_fields = ["id", "label", "inputPorts", "outputPorts", "blockLibrary", "blockType", "properties"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields in HighLevelBlock: {', '.join(missing)}")
        return cls(
            id=data["id"],
            label=data["label"],
            input_ports=data["inputPorts"],
            output_ports=data["outputPorts"],
            block_library=data["blockLibrary"],
            block_type=data["blockType"],
            properties=data["properties"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "inputPorts": self.input_ports,
            "outputPorts": self.output_ports,
            "blockLibrary": self.block_library,
            "blockType": self.block_type,
            "properties": self.properties,
        }