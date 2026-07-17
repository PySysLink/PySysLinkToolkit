from enum import Enum
import json

from pysyslink_toolkit.PortType import PortType



class SubsystemRenderInformation:
    """
    Render information for a subsystem.
    """
    text: str = "No text"

    # New properties for dimensions
    default_width: float = 120.0
    default_height: float = 50.0
    min_width: float = 60.0
    min_height: float = 25.0
    max_width: float = 360.0
    max_height: float = 150.0

    input_ports: int = 1
    output_ports: int = 1

    input_port_types: list[PortType] = []
    output_port_types: list[PortType] = []

    def to_dict(self):
        return {
            "text": self.text,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "input_ports": self.input_ports,
            "output_ports": self.output_ports,
            "input_port_types": [pt.to_dict() for pt in self.input_port_types],
            "output_port_types": [pt.to_dict() for pt in self.output_port_types]
        }

    def to_json(self):
        return json.dumps(self.to_dict())
