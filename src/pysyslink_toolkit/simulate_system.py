import faulthandler
import re
import subprocess; faulthandler.enable()
import json
import time
import yaml
from typing import Callable, Any    
import os



async def simulate_system(
    system_yaml_path: str,
    sim_options_yaml_path: str,
    display_callback: Callable = None
) -> dict:
    """
    Simulate a system using PySysLinkBase Python bindings.

    Args:
        system_yaml_path: Path to the system YAML file.
        sim_options_yaml_path: Path to the simulation options YAML file.
        display_callback: Function called as display is updated: (block_id, time, value).

    Returns:
        The simulation output object.
    """

    cmd = ["PySysLinkBase", "--verbose"]

    # if verbose:
    #     cmd.append("--verbose")

    cmd.extend([system_yaml_path, sim_options_yaml_path])

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
    
    return "Done"
       # Save output to YAML
    # with open(output_filename, "r") as f:
    #     signals = json.load(f)
    #     # for signal_group in signals:
    #     #     for signal in signals[signal_group]:
    #     #         print("--------")
    #     #         print(signal_group)
    #     #         print(signal)
    #     #         print(signals[signal_group][signal])
    #     return signals
    
    # return result.stdout
    