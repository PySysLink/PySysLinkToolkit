

from enum import Enum
import os
import runpy
from typing import Any, Dict, List, Optional, Tuple
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock


class Orientation(Enum):
    Horizontal = "Horizontal"
    Vertical = "Vertical"
    
    @classmethod
    def from_string(cls, value: str) -> "Orientation":
        if value == "Horizontal":
            return Orientation.Horizontal
        elif value == "Vertical":
            return Orientation.Vertical
        else:
            raise ValueError(f"Invalid orientation value: {value}")

class IntermediateSegment:
    def __init__(self, id: str, orientation: Orientation, xOrY: float):
        self.id = id
        self.orientation = orientation
        self.xOrY = xOrY
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntermediateSegment":
        if not all(k in data for k in ("id", "orientation", "xOrY")):
            missing = [k for k in ("id", "orientation", "xOrY") if k not in data]
            raise ValueError(f"Missing fields in IntermediateSegment: {', '.join(missing)}")
        return cls(
            id=data["id"],
            orientation=Orientation.from_string(data["orientation"]),
            xOrY=float(data["xOrY"])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "orientation": self.orientation.value, "xOrY": self.xOrY}

class LinkData:
    def __init__(
        self,
        id: str,
        source_id: str,
        source_port: int,
        target_id: str,
        target_port: int,
        intermediate_segments: List[IntermediateSegment]
    ):
        self.id = id
        self.source_id = source_id
        self.source_port = source_port
        self.target_id = target_id
        self.target_port = target_port
        self.intermediate_segments = intermediate_segments

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        parameter_environment_namespace: Dict[str, Any],
    ) -> "LinkData":
        required = [
            "id", "sourceId", "sourcePort",
            "targetId", "targetPort",
            "intermediateSegments"
        ]
        missing = [f for f in required if f not in data]
        if missing:
            raise ValueError(f"Missing fields in LinkData: {', '.join(missing)}")

        # parse intermediate nodes
        segments = [
            IntermediateSegment.from_dict(n)
            for n in data["intermediateSegments"]
        ]


        return cls(
            id=data["id"],
            source_id=data["sourceId"],
            source_port=int(data["sourcePort"]),
            target_id=data["targetId"],
            target_port=int(data["targetPort"]),
            intermediate_segments=segments
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sourceId": self.source_id,
            "sourcePort": self.source_port,
            "targetId": self.target_id,
            "targetPort": self.target_port,
            "intermediateSegments": [n.to_dict() for n in self.intermediate_segments]
        }

class HighLevelSystem:
    def __init__(
        self,
        simulation_configuration: str,
        initialization_python_script_path: str,
        toolkit_configuration_path: str,
        blocks: Optional[List[HighLevelBlock]],
        links: Optional[List[LinkData]]
    ):
        self.simulation_configuration = simulation_configuration
        self.initialization_python_script_path = initialization_python_script_path
        self.toolkit_configuration_path = toolkit_configuration_path
        self.blocks = blocks
        self.links = links
        
    @classmethod
    def from_dict(
        cls,
        reference_path_or_file: str,
        data: Dict[str, Any],
    ) -> Tuple["HighLevelSystem", Dict[str, Any]]:
        required = [
            "simulation_configuration",
            "initialization_python_script_path",
            "toolkit_configuration_path",
            "blocks",
            "links"
        ]
        missing = [f for f in required if f not in data]
        if missing:
            raise ValueError(f"Missing fields in HighLevelSystem: {', '.join(missing)}")

        initialization_python_script_path = data.get("initialization_python_script_path", None)


        if initialization_python_script_path:
            # Resolve to absolute path if not already absolute
            if not os.path.isabs(initialization_python_script_path):
                pslk_dir = os.path.dirname(os.path.abspath(reference_path_or_file))
                initialization_python_script_path = os.path.normpath(
                    os.path.join(pslk_dir, initialization_python_script_path)
                )
            if os.path.isfile(initialization_python_script_path) and initialization_python_script_path.endswith(".py"):
                try:
                    parameter_environment_namespace = runpy.run_path(initialization_python_script_path, init_globals={})
                except Exception as e:
                    raise RuntimeError(f"Initialization script {initialization_python_script_path} load failed") from e
            else:
                raise FileNotFoundError(f"Initialization script '{initialization_python_script_path}' not found or not a .py file.")
        else:
            print(f"No initialization script provided.")
            parameter_environment_namespace = dict()

        
        # parse blocks
        raw_blocks = data["blocks"]
        blocks = (
            [HighLevelBlock.from_dict(b, parameter_environment_namespace) for b in raw_blocks]
            if raw_blocks is not None
            else None
        )

        # parse links
        raw_links = data["links"]
        links = (
            [LinkData.from_dict(l, parameter_environment_namespace) for l in raw_links]
            if raw_links is not None
            else None
        )


        return (cls(
            simulation_configuration=data["simulation_configuration"],
            initialization_python_script_path=data["initialization_python_script_path"],
            toolkit_configuration_path=data["toolkit_configuration_path"],
            blocks=blocks,
            links=links
        ), parameter_environment_namespace)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_configuration": self.simulation_configuration,
            "initialization_python_script_path": self.initialization_python_script_path,
            "toolkit_configuration_path": self.toolkit_configuration_path,
            "blocks": [b.to_dict() for b in self.blocks] if self.blocks is not None else None,
            "links": [l.to_dict() for l in self.links] if self.links is not None else None,
        }