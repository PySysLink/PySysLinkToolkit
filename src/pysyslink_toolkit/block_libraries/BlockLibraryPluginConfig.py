import ast
import enum
from typing import Any, Dict, Tuple
import yaml


from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation, BlockShape
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure


from dataclasses import dataclass, field
from typing import List, Optional, Union

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
    inputPortNumber: int | str
    outputPortNumber: int | str
    configurationValues: Dict[str, ConfigurationValue] = field(default_factory=dict)
    blockShape: BlockShape = BlockShape.square
    metadata: dict = field(default_factory=dict)

    def get_port_number(self, configuration_values: Dict[str, any]) -> Tuple[int, int]:
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

    blockLibraries: List[BlockLibraryConfig] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


    
    
    

    

