

from enum import Enum
import os
import runpy
from typing import Any, Dict, List, Optional, Tuple
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.PortType import PortCategory, PortType, PortType


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

class SegmentNode:
    def __init__(self, id: str, orientation: Orientation, xOrY: float, children: list["SegmentNode"]):
        self.id = id
        self.orientation = orientation
        self.xOrY = xOrY
        self.children = children

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SegmentNode":
        required = ("id", "orientation", "xOrY", "children")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing fields in SegmentNode: {', '.join(missing)}")

        return cls(
            id=data["id"],
            orientation=Orientation.from_string(data["orientation"]),
            xOrY=float(data["xOrY"]),
            children=[cls.from_dict(c) for c in data.get("children", [])]
        )

    def to_dict(self):
        return {
            "id": self.id,
            "orientation": self.orientation.value,
            "xOrY": self.xOrY,
            "children": [c.to_dict() for c in self.children],
        }

class TargetNodeInfo:
    def __init__(self, target_id: str, port: int, x: float, y: float):
        self.target_id = target_id
        self.port = port
        self.x = x
        self.y = y

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TargetNodeInfo":
        required = ("targetId", "port", "x", "y")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing fields in TargetNodeInfo: {', '.join(missing)}")

        return cls(
            target_id=data["targetId"],
            port=int(data["port"]),
            x=float(data["x"]),
            y=float(data["y"])
        )

    def to_dict(self):
        return {
            "targetId": self.target_id,
            "port": self.port,
            "x": self.x,
            "y": self.y,
        }
class LinkData:
    def __init__(
        self,
        id: str,
        source_id: str,
        source_port: int,
        source_x: float,
        source_y: float,
        segment_node: SegmentNode,
        target_nodes: Dict[str, TargetNodeInfo]
    ):
        self.id = id
        self.source_id = source_id
        self.source_port = source_port
        self.source_x = source_x
        self.source_y = source_y
        self.segment_node = segment_node
        self.target_nodes = target_nodes

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parameter_env=None):
        required = [
            "id", "sourceId", "sourcePort",
            "sourceX", "sourceY",
            "segmentNode", "targetNodes"
        ]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing fields in LinkData: {', '.join(missing)}")

        segment_root = SegmentNode.from_dict(data["segmentNode"])

        targets = {
            seg_id: TargetNodeInfo.from_dict(tgt)
            for seg_id, tgt in data["targetNodes"].items()
        }

        return cls(
            id=data["id"],
            source_id=data["sourceId"],
            source_port=int(data["sourcePort"]),
            source_x=float(data["sourceX"]),
            source_y=float(data["sourceY"]),
            segment_node=segment_root,
            target_nodes=targets,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "sourceId": self.source_id,
            "sourcePort": self.source_port,
            "sourceX": self.source_x,
            "sourceY": self.source_y,
            "segmentNode": self.segment_node.to_dict(),
            "targetNodes": {k: v.to_dict() for k, v in self.target_nodes.items()},
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
    

    def propagate_and_validate_port_types(self) -> None:
        """
        Resolve inherited port types by propagating through links and inheritance groups.
        Modifies block port types in-place.

        Assumptions:
            self.blocks -> list[HighLevelBlock]
            self.links  -> list[LinkData]

            Each block has:
                block.id
                block.input_port_types   -> list[PortType]
                block.output_port_types  -> list[PortType]

        Raises:
            ValueError on unresolved types or incompatible connections.
        """

        if self.blocks is None:
            return

        if self.links is None:
            self.links = []

        # ---------------------------------------------------------
        # Helpers
        # ---------------------------------------------------------

        block_map = {b.id: b for b in self.blocks}

        def is_inherited(pt):
            return pt.port_category == PortCategory.inherited

        def is_known(pt):
            return not is_inherited(pt)

        def clone_type(pt):
            return PortType(
                port_category=pt.port_category,
                signal_value_type=pt.signal_value_type,
                enumeration_name=pt.enumeration_name,
                structure_name=pt.structure_name,
                pointing_object_class_name=pt.pointing_object_class_name,
                other_type_name=pt.other_type_name,
                supported_port_types_for_inheritance=pt.supported_port_types_for_inheritance,
                inheritance_group=pt.inheritance_group,
            )

        def same_type(a: PortType, b: PortType) -> bool:
            return (
                a.port_category == b.port_category
                and a.signal_value_type == b.signal_value_type
                and a.enumeration_name == b.enumeration_name
                and a.structure_name == b.structure_name
                and a.pointing_object_class_name == b.pointing_object_class_name
                and a.other_type_name == b.other_type_name
            )
        
        def is_allowed_inheritance(dst: PortType, src: PortType) -> bool:
            """
            Can dst inherit src?
            """

            # no restriction → always allowed
            if not dst.supported_port_types_for_inheritance:
                return True

            # must match at least one allowed template
            for allowed in dst.supported_port_types_for_inheritance:
                print(f"Checking if {src} can be inherited for {dst} against allowed template {allowed}")
                if allowed == "FullySupportedSignalValueType.Any":
                    if src.port_category == PortCategory.fully_supported_signal_value:
                        return True
                else:
                    if same_type(allowed, src):
                        return True

            return False

        def assign(dst, src):
            """
            Copy concrete type src into inherited dst.
            Returns True if changed.
            """
            if is_known(dst):
                return False

            if is_inherited(src):
                return False
            
            if not is_allowed_inheritance(dst, src):
                raise ValueError(
                    f"Incompatible inheritance: {src} not allowed for port constraints {dst.supported_port_types_for_inheritance}"
                )

            dst.port_category = src.port_category
            dst.signal_value_type = src.signal_value_type
            dst.enumeration_name = src.enumeration_name
            dst.structure_name = src.structure_name
            dst.pointing_object_class_name = src.pointing_object_class_name
            dst.other_type_name = src.other_type_name
            dst.supported_port_types_for_inheritance = (
                src.supported_port_types_for_inheritance
            )

            return True

        def unify(a, b, context=""):
            """
            Make a and b compatible.
            Returns True if something changed.
            """
            # both known
            if is_known(a) and is_known(b):
                if not same_type(a, b):
                    raise ValueError(
                        f"Incompatible port types {a} vs {b}. {context}"
                    )
                return False

            # a known, b inherited
            if is_known(a) and is_inherited(b):
                return assign(b, a)

            # b known, a inherited
            if is_known(b) and is_inherited(a):
                return assign(a, b)

            # both inherited
            return False

        # ---------------------------------------------------------
        # Iterative propagation
        # ---------------------------------------------------------

        changed = True

        while changed:
            changed = False

            # -------------------------------------------------
            # Pass A: propagate through links
            # -------------------------------------------------
            for link in self.links:
                if link.source_id not in block_map:
                    raise ValueError(
                        f"Link source block '{link.source_id}' not found"
                    )

                src_block = block_map[link.source_id]

                if link.source_port >= len(src_block.output_port_types):
                    raise ValueError(
                        f"Invalid source port {link.source_port} "
                        f"on block '{src_block.id}'"
                    )

                src_type = src_block.output_port_types[link.source_port]

                for target in link.target_nodes.values():
                    if target.target_id not in block_map:
                        raise ValueError(
                            f"Link target block '{target.target_id}' not found"
                        )

                    tgt_block = block_map[target.target_id]

                    if target.port >= len(tgt_block.input_port_types):
                        raise ValueError(
                            f"Invalid target port {target.port} "
                            f"on block '{tgt_block.id}'"
                        )

                    tgt_type = tgt_block.input_port_types[target.port]

                    changed |= unify(
                        src_type,
                        tgt_type,
                        context=(
                            f"Connection "
                            f"{src_block.id}.out[{link.source_port}] -> "
                            f"{tgt_block.id}.in[{target.port}]"
                        ),
                    )

            # -------------------------------------------------
            # Pass B: propagate inside each block by inheritance group
            # -------------------------------------------------
            for block in self.blocks:

                groups = {}

                # inputs
                for i, pt in enumerate(block.input_port_types):
                    g = pt.inheritance_group
                    if g not in groups:
                        groups[g] = []
                    groups[g].append(("input", i, pt))

                # outputs
                for i, pt in enumerate(block.output_port_types):
                    g = pt.inheritance_group
                    if g not in groups:
                        groups[g] = []
                    groups[g].append(("output", i, pt))

                # unify all ports inside each group
                for group_id, ports in groups.items():
                    known = None

                    for _, _, pt in ports:
                        if is_known(pt):
                            if known is None:
                                known = pt
                            else:
                                if not same_type(known, pt):
                                    raise ValueError(
                                        f"Conflicting inherited group "
                                        f"{group_id} on block '{block.id}'"
                                    )

                    if known is not None:
                        for _, _, pt in ports:
                            changed |= unify(
                                known,
                                pt,
                                context=(
                                    f"Block '{block.id}' "
                                    f"group {group_id}"
                                ),
                            )

        # ---------------------------------------------------------
        # Final unresolved check
        # ---------------------------------------------------------
        for block in self.blocks:

            for i, pt in enumerate(block.input_port_types):
                if is_inherited(pt):
                    raise ValueError(
                        f"Could not resolve input port type "
                        f"{block.id}.in[{i}]"
                    )

            for i, pt in enumerate(block.output_port_types):
                if is_inherited(pt):
                    raise ValueError(
                        f"Could not resolve output port type "
                        f"{block.id}.out[{i}]"
                    )