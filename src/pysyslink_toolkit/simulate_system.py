import faulthandler
import re
import subprocess; faulthandler.enable()
import json
import time
import pysyslink_base
import yaml
from typing import Callable, Any    
import os



async def simulate_system(
    system_yaml_path: str,
    sim_options_yaml_path: str,
    plugin_configuration: dict[str, Any],
    display_callback: Callable[[pysyslink_base.ValueUpdateBlockEvent], None] = None,
    plugin_dir: str | list[str] = "/usr/local/lib/pysyslink_plugins/block_type_supports/"    
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

    print(f"Sim options yaml path: {sim_options_yaml_path}")
    with open(sim_options_yaml_path, 'r') as stream:
        sim_opts = yaml.safe_load(stream)
    print(f"Sim options: {sim_opts}")

    if type(plugin_dir) == str:
        plugin_dir = [plugin_dir]

    options = {
        "StartTime": sim_opts.get("start_time", 0.0),
        "StopTime": sim_opts.get("stop_time", 10.0),
        "RunInNaturalTime": sim_opts.get("run_in_natural_time", False),
        "NaturalTimeSpeedMultiplier": sim_opts.get(
            "natural_time_speed_multiplier", 1.0
        ),
        "SolversConfiguration": sim_opts.get("solvers_configuration", {}),
        "BlockIdsInputOrOutputAndIndexesToLog": sim_opts.get(
            "block_ids_input_or_output_and_indexes_to_log", []
        ),
        "PluginDirs": plugin_dir,
        "PluginConfiguration": plugin_configuration,
        "SaveToJson": True,

    }

    output_filename = sim_opts.get("simulation_output_filename")

    if output_filename:
        if not os.path.isabs(output_filename):
            system_dir = os.path.dirname(system_yaml_path)
            output_filename = os.path.normpath(
                os.path.join(system_dir, output_filename)
            )
    else:
        output_filename = os.path.join(
            os.path.dirname(system_yaml_path),
            "simulation_output.json"
        )

    options["OutputJsonFile"] = output_filename


    options_yaml_path_relative = "lowLevelOptions.yaml" 
    system_dir = os.path.dirname(system_yaml_path)
    options_yaml_path = os.path.normpath(
        os.path.join(system_dir, options_yaml_path_relative)
    )
    with open(options_yaml_path, "w") as f:
        yaml.safe_dump(options, f, sort_keys=False)

    cmd = ["PySysLinkBase", "--verbose"]

    # if verbose:
    #     cmd.append("--verbose")

    cmd.extend([system_yaml_path, options_yaml_path])

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    with open("stdout.txt", "w") as f:
        f.write(result.stdout)
    with open("stderr.txt", "w") as f:
        f.write(result.stderr)

    if result.returncode != 0:
        
        raise RuntimeError(
            "PySysLinkBase failed\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

       # Save output to YAML
    with open(output_filename, "r") as f:
        signals = json.load(f)
        # for signal_group in signals:
        #     for signal in signals[signal_group]:
        #         print("--------")
        #         print(signal_group)
        #         print(signal)
        #         print(signals[signal_group][signal])
        return signals
    
    return result.stdout
    