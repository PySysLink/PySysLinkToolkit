import json
import yaml
import pathlib
from typing import Dict, Any, List
from pysyslink_toolkit.HighLevelBlock import HighLevelBlock
from pysyslink_toolkit.LowLevelBlockStructure import LowLevelBlock, LowLevelLink, LowLevelBlockStructure
from pysyslink_toolkit.load_plugins import load_plugins_from_paths

def compile_high_level_block(block: HighLevelBlock, plugins) -> LowLevelBlockStructure:
    for plugin in plugins:
        try:
            return plugin.compile_block(block)
        except NotImplementedError:
            continue
    raise RuntimeError(f"No plugin could compile block: {block.block_type}")

def format_property_value(prop_type, value):
    if prop_type == "int":
        return str(int(value))
    elif prop_type == "float":
        return f"{float(value):.1f}"
    elif prop_type == "double":
        return f"{float(value):.1f}"
    elif prop_type == "float[]":
        return [f"{float(v):.1f}" for v in value]
    elif prop_type == "double[]":
        return [f"{float(v):.1f}" for v in value]
    elif prop_type == "int[]":
        return [str(int(v)) for v in value]
    else:
        return value

def serialize_block(block: LowLevelBlock) -> dict:
    d = block.to_dict()
    if "properties" in d:
        for k, v in d["properties"].items():
            if isinstance(v, dict) and "type" in v and "value" in v:
                d["properties"][k]["value"] = format_property_value(v["type"], v["value"])
    return d

def compile_pslk_to_yaml(pslk_path: str, config_path: str, output_yaml_path: str):
    # Load the .pslk file (JSON)
    with open(pslk_path, "r") as f:
        system_json = json.load(f)

    # Load plugins
    config = yaml.safe_load(open(config_path))
    plugin_paths = config.get("plugin_paths", [])
    plugins = load_plugins_from_paths(plugin_paths)

    # Compile each high-level block
    block_structs: Dict[str, LowLevelBlockStructure] = {}
    for block_data in system_json.get("blocks", []):
        block = HighLevelBlock.from_dict(block_data)
        ll_struct = compile_high_level_block(block, plugins)
        block_structs[block.id] = ll_struct

    # Collect all low-level blocks and links
    all_blocks: List[LowLevelBlock] = []
    all_links: List[LowLevelLink] = []
    port_maps: Dict[str, Dict[str, Any]] = {}

    for block_id, struct in block_structs.items():
        all_blocks.extend(struct.blocks)
        all_links.extend(struct.links)
        port_maps[block_id] = struct.port_map

    # Now resolve high-level links to low-level links using port maps
    link_idx = 1
    for link in system_json.get("links", []):
        src_id = link["sourceId"]
        src_port = link["sourcePort"]
        tgt_id = link["targetId"]
        tgt_port = link["targetPort"]

        src_map = port_maps.get(src_id, {})
        tgt_map = port_maps.get(tgt_id, {})
        src_ll = src_map.get(("output", src_port))
        tgt_ll = tgt_map.get(("input", tgt_port))
        if not src_ll or not tgt_ll:
            raise RuntimeError(f"Cannot resolve link: {link}")

        src_block_id, src_port_idx = src_ll
        tgt_block_id, tgt_port_idx = tgt_ll

        ll_link = LowLevelLink(
            id=link.get("id", f"link{link_idx}"),
            name=link.get("id", f"link{link_idx}"),
            source_block_id=src_block_id,
            source_port_idx=src_port_idx,
            destination_block_id=tgt_block_id,
            destination_port_idx=tgt_port_idx,
        )
        all_links.append(ll_link)
        link_idx += 1

    # Prepare YAML output with formatted properties
    output = {
        "Blocks": [serialize_block(block) for block in all_blocks],
        "Links": [link.to_dict() for link in all_links],
    }

    with open(output_yaml_path, "w") as f:
        yaml.dump(output, f, sort_keys=False)

# Example usage:
# compile_pslk_to_yaml("test_json.pslk", "toolkit_config.yaml", "output_system.yaml")