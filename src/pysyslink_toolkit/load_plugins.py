import importlib.util
import pathlib
import inspect
from pysyslink_toolkit.Plugin import Plugin
import yaml

def load_plugins_from_paths(plugin_root_paths) -> list[Plugin]:
    plugins = []
    for root in plugin_root_paths:
        root_path = pathlib.Path(root)
        for yaml_file in root_path.glob("*/**/*.pslkp.yaml"):
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)
            python_filename = config["pythonFilename"]
            py_path = yaml_file.parent / python_filename
            module_name = py_path.stem
            try: 
                plugins.append(load_plugin_from_file(py_path, module_name, config))
            except ImportError as e:
                print("Error loading plugin: {}".format(e.msg))

            
    return plugins

def load_plugin_from_file(path: pathlib.Path, module_name: str, yaml_config: dict) -> Plugin:

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find a subclass of Plugin in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Plugin) and obj is not Plugin:
            return obj(yaml_config)  # Instantiate and return the plugin

    raise ImportError(f"No subclass of Plugin found in {path}")

