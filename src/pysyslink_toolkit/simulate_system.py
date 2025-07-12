import faulthandler
import re; faulthandler.enable()
import json
import time
import pysyslink_base
import yaml
from typing import Callable, Any    

async def simulate_system(
    system_yaml_path: str,
    sim_options_yaml_path: str,
    display_callback: Callable[[pysyslink_base.ValueUpdateBlockEvent], None] = None,
    plugin_dir: str | list[str] = "/usr/local/lib/pysyslink_plugins/block_type_supports/",
    plugin_configuration: dict[str, Any] = {"BasicCppSupport/libraryPluginPath": "/usr/local/lib/pysyslink_plugins"}
) -> dict:
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
    try:
        pysyslink_base.SpdlogManager.configure_default_logger()
    except:
        pass
    pysyslink_base.SpdlogManager.set_log_level(pysyslink_base.LogLevel.debug)

    # Block events handler (for display updates)
    block_events_handler = pysyslink_base.BlockEventsHandler()
    print(pysyslink_base.BlockEventsHandler.register_value_update_block_event_callback)
    block_events_handler.register_value_update_block_event_callback(display_callback)

    # Load plugins
    plugin_loader = pysyslink_base.BlockTypeSupportPluginLoader()

    if isinstance(plugin_dir, str):
        plugin_dir = [plugin_dir]
    
    for dir in plugin_dir:
        block_factories = plugin_loader.load_plugins(dir, plugin_configuration)
    
    print(system_yaml_path)


    # Parse the simulation model
    simulation_model = pysyslink_base.ModelParser.parse_from_yaml(
                        system_yaml_path, block_factories, block_events_handler
                    )

    block_chains = simulation_model.get_direct_block_chains()

    print("Block chains acquired")

    ordered_blocks = simulation_model.order_block_chains_onto_free_order(block_chains)

    print("Blocks ordered")

    # Propagate sample times
    simulation_model.propagate_sample_times()

    print("Simulation times propagated")

    # Load simulation options from YAML
    with open(sim_options_yaml_path, "r") as f:
        # This follows https://stackoverflow.com/questions/58434563/difference-between-yaml-load-and-yaml-safeloader-in-pyyaml to fix floating point on scientific notation
        loader = yaml.SafeLoader
        loader.add_implicit_resolver(
            u'tag:yaml.org,2002:float',
            re.compile(u'''^(?:
            [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
            |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
            |\\.[0-9_]+(?:[eE][-+][0-9]+)?
            |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
            |[-+]?\\.(?:inf|Inf|INF)
            |\\.(?:nan|NaN|NAN))$''', re.X),
            list(u'-+0123456789.'))
        sim_opts_dict = yaml.load(f, Loader=loader)

    simulation_options = pysyslink_base.SimulationOptions()
    simulation_options.start_time = sim_opts_dict.get("start_time", 0.0)
    simulation_options.stop_time = sim_opts_dict.get("stop_time", 10.0)
    simulation_options.run_in_natural_time = sim_opts_dict.get("run_in_natural_time", False)
    simulation_options.natural_time_speed_multiplier = sim_opts_dict.get("natural_time_speed_multiplier", 1)
    simulation_options.block_ids_input_or_output_and_indexes_to_log = sim_opts_dict.get(
        "block_ids_input_or_output_and_indexes_to_log", []
    )
    simulation_options.solvers_configuration = sim_opts_dict.get("solvers_configuration", {})

    output_filename = sim_opts_dict.get("simulation_output_filename")
    

    # Create and run simulation
    simulation_manager = pysyslink_base.SimulationManager(simulation_model, simulation_options)
    simulation_output = simulation_manager.run_simulation()

    # Save output to YAML
    with open(output_filename, "w") as f:
        all_signals = {}
        for signal_group, signals in simulation_output.signals.items():
            all_signals[signal_group] = {}
            for signal_name, signal_obj in signals.items():
                typed_signal = signal_obj.try_cast_to_typed()
                print("Signal group: {}, signal name: {}".format(signal_group, signal_name))
                all_signals[signal_group][signal_name] = {
                    "times": getattr(typed_signal, "times", []),
                    "values": getattr(typed_signal, "values", [])
                }
        json.dump(all_signals, f, indent=2)
        return all_signals


    



if __name__ == "__main__":
    import os

    # Use test data files for debugging
    test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "data")
    system_yaml_path = os.path.join(test_dir, "simulable_system.yaml")
    sim_options_yaml_path = os.path.join(test_dir, "sim_options.yaml")
    output_yaml_path = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "test_outputs", "output_debug_simulation.yaml")

    os.makedirs(os.path.dirname(output_yaml_path), exist_ok=True)

    def debug_display_callback(event):
        print("[Python]:{},{},{}".format(event.value_id, event.simulation_time, event.value))

    simulate_system(
        system_yaml_path,
        sim_options_yaml_path,
        output_yaml_path,
        display_callback=debug_display_callback
    )
    print("outside")
