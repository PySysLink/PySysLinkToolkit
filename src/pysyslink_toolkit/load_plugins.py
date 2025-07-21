import importlib.util
import pathlib
import inspect
from typing import Any, Dict
from pysyslink_toolkit.CoreBlockPlugin import CoreBlockPlugin
from pysyslink_toolkit.Plugin import Plugin
import yaml
from pysyslink_toolkit.TextFileManager import _load_config



def load_plugins_from_paths(config_path, include_default_paths=True) -> list[Plugin]:
    plugins: list[Plugin] = []
    toolkit_config = _load_config(config_path)
    plugin_root_paths = toolkit_config.get("plugin_paths", [])
    print(plugin_root_paths)
    if include_default_paths:
        plugin_root_paths.append("/usr/local/lib/pysyslink_plugins")
    print(plugin_root_paths)
    for root in plugin_root_paths:
        root_path = pathlib.Path(root)
        if not root_path.is_absolute():
            root_path = pathlib.Path(config_path).parent / root_path
            root_path = root_path.resolve()
        for yaml_file in root_path.glob("**/*.pslkp.yaml"):
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)
            if config["pluginType"] == "highLevelBlockLibrary":
                python_filename = config["pythonFilename"]
                py_path = yaml_file.parent / python_filename
                module_name = py_path.stem # py_path.stem is correct, it returns the module name
                try: 
                    plugins.append(load_plugin_from_file(py_path, module_name, config, toolkit_config))
                except ImportError as e:
                    print("Error loading plugin: {}".format(e.msg))
            elif config["pluginType"] == "coreBlockLibrary":
                plugins.append(CoreBlockPlugin(config, toolkit_config))

            
    return plugins

def load_plugin_from_file(path: pathlib.Path, module_name: str, yaml_config: dict, toolkit_config: dict) -> Plugin:

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find a subclass of Plugin in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Plugin) and obj is not Plugin:
            return obj(yaml_config, toolkit_config)  # Instantiate and return the plugin

    raise ImportError(f"No subclass of Plugin found in {path}")

