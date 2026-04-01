import enum
from typing import Any, Dict
import yaml


from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation, BlockShape
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure


from dataclasses import dataclass, field
from typing import List, Optional, Union


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


    
    
    

    

