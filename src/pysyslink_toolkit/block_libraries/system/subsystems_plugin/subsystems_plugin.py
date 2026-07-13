import json
import os

from matplotlib import pyplot as plt
import yaml
import pysyslink_toolkit
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelLink, LowLevelBlockStructure
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock

import mpld3


class SubsystemPlugin(pysyslink_toolkit.BlockLibraryPlugin):   
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        port_map = {}


        return LowLevelBlockStructure([], [], port_map)

