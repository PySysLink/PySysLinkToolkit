from typing import Any, Dict, List, Optional

from pysyslink_toolkit.PortType import PortType

class HighLevelBlock:
    def __init__(
        self,
        id: str,
        label: str,
        input_ports: int,
        input_port_types: List[PortType],
        output_ports: int,
        output_port_types: List[PortType],
        block_library: str,
        block_type: str,
        properties: Dict[str, Dict[str, Any]]
    ):
        self.id = id
        self.label = label
        self.input_ports = input_ports
        self.input_port_types = input_port_types
        self.output_ports = output_ports
        self.output_port_types = output_port_types
        self.block_library = block_library
        self.block_type = block_type
        self.properties = properties

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        parameter_environment_namespace: Dict[str, Any]
    ) -> "HighLevelBlock":
        # Required fields validation
        required_fields = [
            "id", "label", "inputPorts", "outputPorts", "inputPortTypes", "outputPortTypes",
            "blockLibrary", "blockType", "properties"
        ]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields in HighLevelBlock: {', '.join(missing)}")

        # Type and format checks
        try:
            block_id = str(data["id"])
            label = str(data["label"])
            input_ports = int(data["inputPorts"])
            input_port_types = [PortType.from_dict(data_i) for data_i in data["inputPortTypes"]]
            output_ports = int(data["outputPorts"])
            output_port_types = [PortType.from_dict(data_o) for data_o in data["outputPortTypes"]]
            block_library = str(data["blockLibrary"])
            block_type = str(data["blockType"])
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid type for one of the HighLevelBlock fields: {e}")

        raw_props = data["properties"]
        if not isinstance(raw_props, dict):
            raise ValueError("`properties` must be a dictionary")

        parsed_props: Dict[str, Dict[str, Any]] = {}
        for key, entry in raw_props.items():
            if not isinstance(entry, dict) or "type" not in entry or "value" not in entry:
                raise ValueError(f"Property entry for '{key}' must be a dict with 'type' and 'value'")

            ptype = entry.get("type")
            value = entry.get("value")

            # Evaluate expressions when appropriate
            if isinstance(value, str) and ptype != "string" and not ptype.startswith("enum(") and not ptype.startswith("options("):
                try:
                    evaluated = eval(
                        value,
                        parameter_environment_namespace,
                        parameter_environment_namespace
                    )
                except Exception as e:
                    raise ValueError(f"Error evaluating property '{key}' of type '{ptype}': {e}")
            else:
                evaluated = value

            parsed_props[key] = {
                "type": ptype,
                "value": evaluated
            }

        return cls(
            id=block_id,
            label=label,
            input_ports=input_ports,
            input_port_types=input_port_types,
            output_ports=output_ports,
            output_port_types=output_port_types,
            block_library=block_library,
            block_type=block_type,
            properties=parsed_props,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "inputPorts": self.input_ports,
            "inputPortTypes": self.input_port_types,
            "outputPorts": self.output_ports,
            "outputPortTypes": self.output_port_types,
            "blockLibrary": self.block_library,
            "blockType": self.block_type,
            "properties": self.properties,
        }