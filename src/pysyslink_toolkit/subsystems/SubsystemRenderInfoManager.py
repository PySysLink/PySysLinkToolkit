

from typing import Any, Dict, Tuple

from pysyslink_toolkit.HighLevelSystem import HighLevelSystem
from pysyslink_toolkit.PortType import PortCategory, PortType
from pysyslink_toolkit.SubsystemRenderInformation import SubsystemRenderInformation
from pysyslink_toolkit.toolkit_config.ToolkitConfig import ToolkitConfig

def get_subsystem_port_numbers(subsystem_data: Dict[str, Any], pslk_path: str) -> Tuple[int, int]:
    json_data = subsystem_data.get("jsonData", {})
    blocks = json_data.get("blocks", [])

    input_count = 0
    output_count = 0

    for block in blocks:
        block_type = block.get("blockType")
        if block_type == "input_port":
            input_count += 1
        elif block_type == "output_port":
            output_count += 1

    return input_count, output_count


def get_subsystem_port_types(subsystem_data: Dict[str, Any], pslk_path: str) -> Tuple[PortType, PortType]:
    """
    Get the input and output port types for a subsystem.
    """
    input_port_number, output_port_number = get_subsystem_port_numbers(subsystem_data, pslk_path)

    input_port_types = [PortType(port_category=PortCategory.inherited, supported_port_types_for_inheritance=['FullySupportedSignalValueType.Any'])] * input_port_number
    output_port_types = [PortType(port_category=PortCategory.inherited, supported_port_types_for_inheritance=['FullySupportedSignalValueType.Any'])] * output_port_number

    return input_port_types, output_port_types

def _get_subsystem_render_information(toolkit_config: ToolkitConfig, parameter_environment_dict: Dict[str, Any], subsystem_data: Dict[str, Any], pslk_path: str) -> SubsystemRenderInformation:
    """
    Return render information for a subsystem.
    """
    render_information = SubsystemRenderInformation()
    render_information.text = subsystem_data.get("label", "No label")

    render_information.input_ports, render_information.output_ports = get_subsystem_port_numbers(subsystem_data, pslk_path)
    render_information.input_port_types, render_information.output_port_types = get_subsystem_port_types(subsystem_data, pslk_path)

    return render_information

