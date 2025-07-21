import os
import pytest
import yaml
from pysyslink_toolkit import api
import asyncio

TEST_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@pytest.fixture
def config_path():
    return os.path.join(TEST_DIR, "data", "toolkit_config.yaml")

@pytest.fixture
def pslk_path():
    return os.path.join(TEST_DIR, "data", "dummy.pslk")

@pytest.fixture
def pslk_path_with_parameters():
    return os.path.join(TEST_DIR, "data", "parse_parameters.pslk")

@pytest.fixture
def output_yaml_path(request):
    OUTPUT_DIR = os.path.join(TEST_DIR, "test_outputs")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    test_name = request.node.name  # This gives you the test function name
    return os.path.join(OUTPUT_DIR, f"output_{test_name}.yaml")

def test_compile_system(config_path, pslk_path, output_yaml_path):
    result = api.compile_system(config_path, pslk_path, str(output_yaml_path))
    assert result == "success"
    with open(output_yaml_path) as f:
        content = f.read()
        assert "Blocks:" in content

def test_compile_system_with_parameters(config_path, pslk_path_with_parameters, output_yaml_path):
    result = api.compile_system(config_path, pslk_path_with_parameters, str(output_yaml_path))
    assert result == "success"
    with open(output_yaml_path) as f:
        content = f.read()
        assert "Blocks:" in content

def test_neuron_block_compilation(config_path, output_yaml_path):
    # Paths to input and expected output
    test_dir = os.path.dirname(__file__)
    input_pslk = os.path.join(test_dir, "data", "neuron_test.pslk")
    expected_yaml = os.path.join(test_dir, "data", "neuron_output.yaml")
    output_yaml = output_yaml_path

    # Run the compilation
    result = api.compile_system(config_path, input_pslk, str(output_yaml))
    assert result == "success"

    # Load and compare YAMLs
    with open(output_yaml) as f:
        actual = yaml.safe_load(f)
    with open(expected_yaml) as f:
        expected = yaml.safe_load(f)

    assert actual == expected

def test_get_available_block_libraries(config_path):
    libs = api.get_available_block_libraries(config_path)
    assert isinstance(libs, list)
    assert any(lib.name == "dummy_library" for lib in libs)

def test_get_block_render_information(config_path):
    block_data = {
        "id": "block1",
        "label": "Test Block",
        "inputPorts": 1,
        "outputPorts": 1,
        "blockLibrary": "dummy_library",
        "blockType": "dummy",
        "properties": {}
    }
    test_dir = os.path.dirname(__file__)
    input_pslk = os.path.join(test_dir, "data", "neuron_test.pslk")

    info = api.get_block_render_information(config_path, block_data, input_pslk)
    assert info is not None

def test_get_block_render_information_with_parameters(config_path):
    block_data = {
        "id": "nx0MITpddR4PS825bmSZzPmHFqtCAu6b",
        "blockLibrary": "core_BasicBlocks",
        "blockType": "Constant",
        "label": "Constant",
        "x": 707.0833333333333,
        "y": 518.5538194444446,
        "inputPorts": 0,
        "outputPorts": 1,
        "properties": {
            "Value": {
            "type": "float",
            "value": "max(4, 5) - 4/3"
            }
        }
    }
    test_dir = os.path.dirname(__file__)
    input_pslk = os.path.join(test_dir, "data", "neuron_test.pslk")
    info = api.get_block_render_information(config_path, block_data, input_pslk)
    assert info is not None

def test_get_block_render_information_basic_block(config_path):
    block_data = {
        "id":"InIvNfx88BzB6k7e7uL2ODxhMcVDWbH0",
        "blockLibrary":"core_BasicBlocks",
        "blockType":"Constant",
        "label":"Constant",
        "x":90,
        "y":146,
        "inputPorts":1,
        "outputPorts":1,"properties":{
            "Value": {
                "type": "float",
                "value": 1
            }
        }
    }
    test_dir = os.path.dirname(__file__)
    input_pslk = os.path.join(test_dir, "data", "neuron_test.pslk")
    info = api.get_block_render_information(config_path, block_data, input_pslk)
    print(info.to_dict())
    assert info is not None
    assert info.input_ports == 0
    assert info.output_ports == 1
    assert info.text == "Constant"


def test_simulation_runs_and_callbacks(config_path):
    test_dir = os.path.dirname(__file__)
    system_yaml = os.path.join(test_dir, "data", "simulable_system.yaml")
    sim_options_yaml = os.path.join(test_dir, "data", "sim_options.yaml")
    output_json = os.path.join(OUTPUT_DIR, "output_test_simulation_runs_and_callbacks.json")

    # Prepare a callback to record display updates
    callback_calls = []

    def display_callback(event):
        callback_calls.append((event.value_id, event.simulation_time, event.value))

    # Run the simulation
    result = asyncio.run(
        api.run_simulation(
            config_path,
            system_yaml,
            sim_options_yaml,
            display_callback=display_callback
        )
    )

    assert os.path.exists(output_json)
    # The simulation result object should not be None
    assert result is not None
    # The callback should have been called at least once
    assert len(callback_calls) > 0