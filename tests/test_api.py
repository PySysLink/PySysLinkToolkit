import os
import pytest
import yaml
from pysyslink_toolkit import api

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
    assert any(lib["name"] == "dummy_library" for lib in libs)

def test_get_block_render_information(config_path):
    block_data = {
        "id": "block1",
        "label": "Test Block",
        "inputPorts": 1,
        "outputPorts": 1,
        "block_library": "dummy_library",
        "block_type": "dummy",
        "properties": {}
    }
    info = api.get_block_render_information(config_path, block_data)
    assert info is not None