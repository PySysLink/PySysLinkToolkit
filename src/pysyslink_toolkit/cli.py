import argparse
import asyncio
import json
import os

import yaml
from pysyslink_toolkit.api import (
    compile_system,
    compile_and_run_simulation
)


import os

def resolve_absolute_path(path: str, base_dir: str | None = None) -> str:
    """
    Resolve a path to an absolute normalized path.
    If relative, resolve against base_dir (or cwd if omitted).
    """
    if os.path.isabs(path):
        return os.path.normpath(path)

    if base_dir is None:
        base_dir = os.getcwd()

    return os.path.normpath(
        os.path.abspath(
            os.path.join(base_dir, path)
        )
    )

def get_simulation_configuration_path(pslkPath: str):
    """
    Load the simulation configuration from the given PSLK path.
    """
    with open(pslkPath, "r") as f:
        system_json = json.load(f)

    sim_config_path = system_json.get("simulation_configuration", [])
    print(f"Simulation configuration path: {sim_config_path}")

    pslk_dir = os.path.dirname(pslkPath)
    
    return resolve_absolute_path(
        sim_config_path,
        pslk_dir
    )

def get_toolkit_config_path(pslkPath: str) -> str:
    """
    Get the toolkit configuration path from the PSLK file.
    """
    with open(pslkPath, "r") as f:
        try:
            system_json = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Invalid PSLK file format: {e}")
            return None
        
    toolkit_config_path = system_json.get("toolkit_configuration_path", None)

    if toolkit_config_path is None or toolkit_config_path == "":
        raise RuntimeError(
            "No toolkit_configuration_path in PSLK"
        )
    
    pslk_dir = os.path.dirname(pslkPath)

    return resolve_absolute_path(
        toolkit_config_path,
        pslk_dir
    )


def get_output_yaml_path(pslk_path: str) -> str:
    base, ext = os.path.splitext(pslk_path)

    if ext.lower() == ".pslk":
        return base + "_low_level_system.yaml"

    return pslk_path + "_low_level_system.yaml"

def main():
    parser = argparse.ArgumentParser(prog="pysyslink")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("pslk")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("pslk")

    args = parser.parse_args()

    pslk_path = resolve_absolute_path(args.pslk)

    toolkit_path = get_toolkit_config_path(pslk_path)
    output_yaml = get_output_yaml_path(pslk_path)

    if args.command == "compile":
        result = compile_system(
            toolkit_path,
            pslk_path,
            output_yaml
        )
        print(result)

    elif args.command == "run":
        sim_config = get_simulation_configuration_path(
            pslk_path
        )

        result = asyncio.run(
            compile_and_run_simulation(
                toolkit_path,
                pslk_path,
                output_yaml,
                sim_config
            )
        )

        print(result)


if __name__ == "__main__":
    main()