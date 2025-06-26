from typing import Any, Dict

def safe_eval(expr: str, context: Dict[str, Any] = {}) -> Any:
    """Evaluate a Python expression safely in a minimal context."""
    allowed_builtins = {
        'min': min,
        'max': max,
        'abs': abs,
        'sum': sum,
        'len': len,
        'float': float,
        'int': int,
        'range': range,
        # Add math functions if needed
    }
    import math
    safe_globals = {"__builtins__": allowed_builtins, "math": math}
    safe_globals.update(context)
    return eval(expr, safe_globals, {})

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
    def from_dict(cls, data: Dict[str, Any], parameter_environment_namespace: Dict[str, Any]) -> "HighLevelBlock":
        required_fields = ["id", "label", "inputPorts", "outputPorts", "blockLibrary", "blockType", "properties"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields in HighLevelBlock: {', '.join(missing)}")

        raw_props = data["properties"]
        parsed_props = {}

        for key, entry in raw_props.items():
            ptype = entry.get("type")
            value = entry.get("value")

            # Evaluate only if it's a string and not a string-typed property
            if isinstance(value, str) and ptype != "string":
                try:
                    evaluated = eval(value, parameter_environment_namespace, parameter_environment_namespace)
                except Exception as e:
                    raise ValueError(f"Error evaluating property '{key}': {e}")
            else:
                evaluated = value

            parsed_props[key] = {
                "type": ptype,
                "value": evaluated
            }

        return cls(
            id=data["id"],
            label=data["label"],
            input_ports=data["inputPorts"],
            output_ports=data["outputPorts"],
            block_library=data["blockLibrary"],
            block_type=data["blockType"],
            properties=parsed_props,
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