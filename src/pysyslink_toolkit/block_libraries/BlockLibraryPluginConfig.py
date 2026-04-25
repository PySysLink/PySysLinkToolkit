import ast
import enum
from typing import Any, Dict, Tuple
import yaml


from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation, BlockShape
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure


from dataclasses import dataclass, field
from typing import List, Optional, Union

from pysyslink_toolkit.PortType import FullySupportedSignalValueType, PortCategory, PortType, PortTypeConfig
from pysyslink_toolkit.block_libraries.SafeEvaluator import SafeEvaluator

@dataclass
class ConfigurationValue:
    name: str
    defaultValue: Union[float, int, str, List[float], List[int], List[str], None]
    type: str
    metadata: dict = field(default_factory=dict)

@dataclass
class BlockTypeConfig:
    name: str
    inputPortNumber: int | str = "NullForCommonBlock"
    outputPortNumber: int | str = "NullForCommonBlock"

    inputPortTypes: dict[str | int, PortTypeConfig] = field(default_factory=dict)
    outputPortTypes: dict[str | int, PortTypeConfig] = field(default_factory=dict)
    commonBlock: str | None = None
    configurationValues: Dict[str, ConfigurationValue] = field(default_factory=dict)
    blockShape: BlockShape = BlockShape.square
    metadata: dict = field(default_factory=dict)

    def get_port_number(self, configuration_values: Dict[str, any]) -> Tuple[int, int]:
        if self.inputPortNumber == "NullForCommonBlock" or self.outputPortNumber == "NullForCommonBlock":
            raise ValueError("get_port_number called on a common block, or specific block did not override the field correctly")
        
        result = [None, None]
        if type(self.inputPortNumber) is int:
            result[0] = self.inputPortNumber
        else:
            result[0] = self.parse_port_number_expression(self.inputPortNumber, configuration_values)
        
        if type(self.outputPortNumber) is int:
            result[1] = self.outputPortNumber
        else:
            result[1] = self.parse_port_number_expression(self.outputPortNumber, configuration_values)
        
        return tuple(result)
    
    def parse_port_number_expression(self, port_number_expression: str, configuration_values: Dict[str, any]) -> int:
        try:
            tree = ast.parse(port_number_expression, mode="eval")
            evaluator = SafeEvaluator(configuration_values)
            result = evaluator.visit(tree)

            if not isinstance(result, int):
                result = int(result)

            if result < 0:
                raise ValueError("Port number cannot be negative")

            return result

        except Exception as e:
            raise ValueError(
                f"Error parsing expression '{port_number_expression}': {e}"
            )

    def get_port_types(self, configuration_values: Dict[str, Any]) -> Tuple[List[PortType], List[PortType]]:
        """
        Resolve input/output PortTypeConfig into concrete PortType objects.
        Returns:
            (input_port_types, output_port_types)
        """
        input_count, output_count = self.get_port_number(configuration_values)

        input_types = self._resolve_port_type_dict(
            self.inputPortTypes, input_count, configuration_values
        )

        output_types = self._resolve_port_type_dict(
            self.outputPortTypes, output_count, configuration_values
        )

        return input_types, output_types

    def _resolve_port_type_dict(self, configs: Dict[str | int, PortTypeConfig], expected_count: int, configuration_values: Dict[str, Any]) -> List[PortType]:
        """
        Resolve a port-type dictionary into a list ordered by port index.

        Priority:
            explicit index > others > all
        """

        if expected_count < 0:
            raise ValueError("Port count cannot be negative")

        # initialize unresolved ports
        result: List[PortType | None] = [None] * expected_count

        # Resolve defaults first
        all_cfg = configs.get("all")
        others_cfg = configs.get("others")

        all_type = (
            self._resolve_port_type(all_cfg, configuration_values)
            if all_cfg is not None
            else None
        )

        others_type = (
            self._resolve_port_type(others_cfg, configuration_values)
            if others_cfg is not None
            else None
        )

        # Apply "all"
        if all_type is not None:
            for i in range(expected_count):
                result[i] = all_type

        # Apply explicit indexes
        for key, cfg in configs.items():

            if key in ("all", "others"):
                continue

            # accept int keys or numeric strings
            if isinstance(key, int):
                idx = key
            elif isinstance(key, str) and key.isdigit():
                idx = int(key)
            else:
                raise ValueError(f"Invalid port type key: {key}")

            if idx < 0 or idx >= expected_count:
                raise ValueError(
                    f"Port index {idx} out of range (0..{expected_count - 1})"
                )

            result[idx] = self._resolve_port_type(cfg, configuration_values)

        # Apply "others" to still unresolved ports
        if others_type is not None:
            for i in range(expected_count):
                if result[i] is None:
                    result[i] = others_type

        # Validate all resolved
        unresolved = [i for i, v in enumerate(result) if v is None]
        if unresolved:
            raise ValueError(
                f"Missing port type definitions for ports: {unresolved}"
            )

        return result

    def _resolve_port_type(self, cfg: PortTypeConfig, configuration_values: Dict[str, Any]) -> PortType:
        """
        Resolve one PortTypeConfig into one PortType.
        """

        category = PortCategory(cfg.port_category)

        return PortType(
            port_category=category,
            signal_value_type=self._resolve_signal_value_type(
                cfg.signal_value_type, configuration_values
            ),
            enumeration_name=self._resolve_string(
                cfg.enumeration_name, configuration_values
            ),
            structure_name=self._resolve_string(
                cfg.structure_name, configuration_values
            ),
            pointing_object_class_name=self._resolve_string(
                cfg.pointing_object_class_name, configuration_values
            ),
            other_type_name=self._resolve_string(
                cfg.other_type_name, configuration_values
            ),
            supported_port_types_for_inheritance=(
                [
                    self._resolve_port_type(x, configuration_values)
                    for x in (cfg.supported_port_types_for_inheritance or [])
                ]
                if cfg.supported_port_types_for_inheritance
                else None
            ),
        )

    def _resolve_signal_value_type(self, value: str | None, configuration_values: Dict[str, Any]) -> FullySupportedSignalValueType | None:
        if value is None:
            return None

        resolved = configuration_values.get(value, value)

        if isinstance(resolved, FullySupportedSignalValueType):
            return resolved

        return FullySupportedSignalValueType(resolved)

    def _resolve_string(self, value: str | None, configuration_values: Dict[str, Any]) -> str | None:
        if value is None:
            return None

        return str(configuration_values.get(value, value))

@dataclass
class BlockLibraryConfig:
    name: str
    blockTypes: List[BlockTypeConfig] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

class BlockLibraryPluginType(enum.Enum):
    CoreBlockLibrary = "coreBlockLibrary"
    HighLevelBlockLibrary = "highLevelBlockLibrary"


@dataclass
class BlockLibraryPluginConfig:
    pluginName: str
    pluginType: BlockLibraryPluginType
    blockType: str

    yaml_filename: str | None

    commonBlocks: List[BlockTypeConfig] = field(default_factory=list)

    blockLibraries: List[BlockLibraryConfig] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


    
    
    

    

