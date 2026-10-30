import json
import os

from matplotlib import pyplot as plt
import yaml
import pysyslink_toolkit
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelBlockStructure
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock

import mpld3


class ScopePlugin(pysyslink_toolkit.BlockLibraryPlugin):   
    def _compile_block(self, high_level_block: HighLevelBlock, pslk_path: str) -> LowLevelBlockStructure:
        port_map = {}
        blocks = []

        for input_port_idx, input_port_type in enumerate(high_level_block.input_port_types):
            display_id = high_level_block.id if input_port_idx == 0 else f"{high_level_block.id}_{input_port_idx}"
            block = LowLevelBlock(
                id=display_id,
                name=f"Scope {high_level_block.label} Display {input_port_idx + 1}",
                block_type="BasicCpp",
                block_class="BasicBlocks/Display",
                input_port_number=1,
                input_port_types=[input_port_type.to_string()],
                output_port_number=0,
                output_port_types=[],
            )
            blocks.append(block)
            port_map[("input", input_port_idx)] = (display_id, 0)

        return LowLevelBlockStructure(blocks, [], port_map)

    def _get_block_html(self, high_level_block, pslk_path):
        with open(pslk_path, "r") as f:
            system_json = json.load(f)

        simulation_configuration_yaml_path = system_json.get("simulation_configuration", [])

        # Resolve to absolute path if not already absolute
        if not os.path.isabs(simulation_configuration_yaml_path):
            pslk_dir = os.path.dirname(os.path.abspath(pslk_path))
            simulation_configuration_yaml_path = os.path.normpath(
                os.path.join(pslk_dir, simulation_configuration_yaml_path)
            )

        with open(simulation_configuration_yaml_path, "r") as f:
            sim_config = yaml.safe_load(f)

        output_filename = sim_config.get("simulation_output_filename")
        if output_filename:
            if not os.path.isabs(output_filename):
                system_dir = os.path.dirname(pslk_path)
                output_filename = os.path.normpath(os.path.join(system_dir, output_filename))
        else:
            output_filename = os.path.join(os.path.dirname(pslk_path), "simulation_output.json")

        if not output_filename:
            return "No simulation output filename found in configuration."

        # # Resolve output file path
        # if not os.path.isabs(output_filename):
        #     output_filename = os.path.join(os.path.dirname(simulation_configuration_yaml_path), output_filename)

        # Read and parse the simulation output file
        if not os.path.exists(output_filename):
            return f"Simulation output file '{output_filename}' not found."

        with open(output_filename, "r") as f:
            output_data = json.load(f)

        # Example: extract all display data for plotting
        displays = output_data.get("Displays", {})
        plot_data = {}
        for display_id, display in displays.items():
            times = display.get("times", [])
            values = display.get("values", [])
            plot_data[display_id] = {"times": times, "values": values}

        fig = plt.figure()
        for input_port_idx in range(high_level_block.input_ports):
            display_id = high_level_block.id if input_port_idx == 0 else f"{high_level_block.id}_{input_port_idx}"
            display = plot_data.get("BasicCppBlock/" + display_id)
            if display is None:
                continue
            plt.plot(
                display["times"],
                display["values"],
                label=f"Input {input_port_idx + 1}",
            )

        if high_level_block.input_ports > 1:
            plt.legend()
        html_str = mpld3.fig_to_html(fig)
        
        return html_str
