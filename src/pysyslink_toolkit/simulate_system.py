import pysyslink_base
import yaml
from typing import Callable, Any

async def simulate_system(
    system_yaml_path: str,
    sim_options_yaml_path: str,
    output_filename: str,
    display_callback: Callable[[str, float, float], None] = None,
    plugin_dir: str = "/usr/local/lib"
) -> Any:
    """
    Simulate a system using PySysLinkBase Python bindings.

    Args:
        system_yaml_path: Path to the system YAML file.
        sim_options_yaml_path: Path to the simulation options YAML file.
        output_filename: Path to save the simulation output YAML.
        display_callback: Function called as display is updated: (block_id, time, value).
        plugin_dir: Directory to search for block type support plugins.

    Returns:
        The simulation output object.
    """
    # Set up logging
    pysyslink_base.SpdlogManager.configure_default_logger()
    pysyslink_base.SpdlogManager.set_log_level(pysyslink_base.LogLevel.info)

    # Block events handler (for display updates)
    class DisplayHandler(pysyslink_base.BlockEventsHandler):
        def on_display_update(self, block_id, time, value):
            if display_callback:
                display_callback(block_id, time, value)

    block_events_handler = DisplayHandler()

    # Load plugins
    plugin_loader = pysyslink_base.BlockTypeSupportPlugingLoader()
    block_factories = plugin_loader.load_plugins(plugin_dir)

    # Parse the simulation model
    simulation_model = pysyslink_base.ModelParser.parse_from_yaml(
        system_yaml_path, block_factories, block_events_handler
    )

    # Load simulation options from YAML
    with open(sim_options_yaml_path, "r") as f:
        sim_opts_dict = yaml.safe_load(f)

    sim_options = pysyslink_base.SimulationOptions()
    sim_options.start_time = sim_opts_dict.get("start_time", 0.0)
    sim_options.stop_time = sim_opts_dict.get("stop_time", 10.0)
    sim_options.run_in_natural_time = sim_opts_dict.get("run_in_natural_time", False)
    sim_options.natural_time_speed_multiplier = sim_opts_dict.get("natural_time_speed_multiplier", 1)
    sim_options.block_ids_input_or_output_and_indexes_to_log = sim_opts_dict.get(
        "block_ids_input_or_output_and_indexes_to_log", []
    )

    # Create and run simulation
    simulation_manager = pysyslink_base.SimulationManager(simulation_model, sim_options)
    simulation_output = simulation_manager.run_simulation()

    # Save output to YAML
    with open(output_filename, "w") as f:
        # You may want to serialize only relevant parts
        yaml.dump(simulation_output.to_dict(), f)

    return simulation_output