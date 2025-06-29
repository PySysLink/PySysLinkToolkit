import json
import os

from matplotlib import pyplot as plt
import yaml
import pysyslink_toolkit
from pysyslink_toolkit.BlockRenderInformation import BlockRenderInformation
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelLink, LowLevelBlockStructure
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock

import mpld3



class NeuronPlugin(pysyslink_toolkit.Plugin):   
    
    def _compile_block(self, high_level_block: HighLevelBlock) -> LowLevelBlockStructure:
        port_map = {}

        block = LowLevelBlock(
            id=high_level_block.id, name=f"Scope {high_level_block.label} Display", block_type="BasicCpp", block_class="BasicBlocks/Display"
        )
        port_map[("input", 0)] = (high_level_block.id, 0)

        return LowLevelBlockStructure([block], [], port_map)
    
    def _get_block_render_information(self, high_level_block):
        render_information = BlockRenderInformation()

        render_information.input_ports =1
        render_information.output_ports = 0

        return render_information
    
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
        plt.plot(plot_data[high_level_block.id]["times"], plot_data[high_level_block.id]["values"])
        html_str = mpld3.fig_to_html(fig)
        
        return html_str
