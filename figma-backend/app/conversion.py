import yaml
from copy import deepcopy
from app.utils import normalize_dims, denormalize_dims
from app.types import Coord, Scene, FigmaFrame, FigmaNode, DSLNode, DSLJson, DSLYaml
from app.utils import rgb_to_hex, hex_to_rgb
from jsondiff import diff, patch
from app.utils import lists_to_dicts, dicts_to_lists, extract_children


def figma_to_json_dsl_node(node: FigmaNode) -> DSLNode:
    """Converts a Figma node to JSON DSL. Includes normalization etc."""
    # TODO: convert types intelligently - color, position, etc.
    # TODO: list to dict, etc.
    output_node = deepcopy(node)
    if node['node'].get('color'):
        figma_color = node['node']['color']
        hex_color = rgb_to_hex(figma_color)
        output_node['node']['color'] = hex_color
    return output_node


def json_dsl_to_figma_node(node: DSLNode) -> FigmaNode:
    """Converts a Figma node to JSON DSL. Includes normalization etc."""
    # TODO: convert types intelligently - color, position, etc.
    # TODO: list to dict, etc.
    output_node = deepcopy(node)
    if node['node'].get('color'):
        hex_color = node['node']['color']
        rgb_color = hex_to_rgb(hex_color)
        output_node['node']['color'] = rgb_color
    return output_node


def figma_to_json_dsl_inner(scene_norm: Scene):
    if type(scene_norm) is list:
        return [figma_to_json_dsl_inner(node) for node in scene_norm]
    elif scene_norm.get('type') in ('FRAME', 'GROUP'):
        scene_norm['node']['children'] = [figma_to_json_dsl_inner(child) for child in scene_norm['node']['children']]
        return scene_norm
    else:
        return figma_to_json_dsl_node(scene_norm)


def figma_to_json_dsl(scene_raw: Scene) -> DSLJson:
    """Converts a Figma scene to JSON DSL. Includes normalization etc."""
    scene_norm = normalize_dims(scene_raw)
    scene_norm = figma_to_json_dsl_inner(scene_norm)
    scene_norm = lists_to_dicts(scene_norm)
    return scene_norm


def json_dsl_to_figma_inner(scene):
    if type(scene) is list:
        return [json_dsl_to_figma_inner(node) for node in scene]
    elif scene.get('type') in ('FRAME', 'GROUP'):
        scene['node']['children'] = [json_dsl_to_figma_inner(child) for child in scene['node']['children']]
        return scene
    else:
        return json_dsl_to_figma_node(scene)


def json_dsl_to_figma(scene: DSLJson) -> Scene:
    """Converts a JSON DSL scene to a Figma scene"""
    scene = dicts_to_lists(scene)
    scene = json_dsl_to_figma_inner(scene)
    scene = extract_children(scene)
    return scene


def figma_to_yaml(scene_raw: Scene) -> str:
    """Converts a Figma scene to YAML. Includes normalization etc."""
    scene_dslj = figma_to_json_dsl(scene_raw)
    scene_dsly = yaml.dump(scene_dslj, sort_keys=False)
    return scene_dsly


def yaml_to_figma(yaml_str: str, tl: Coord, w: int) -> Scene:
    """Converts a yaml_str (gpt3 output) to a Figma scene"""
    scene_dslj = yaml.safe_load(yaml_str)
    scene_figma = json_dsl_to_figma(scene_dslj)
    scene = denormalize_dims(scene_figma, tl, w)
    if not type(scene) is list:
        scene = [scene]
    return scene


def get_scene_diff(a: Scene, b: Scene) -> dict:
    """Returns a diff between two scenes"""
    a, b = figma_to_json_dsl(a), figma_to_json_dsl(b)
    js_diff = diff(a, b)
    return js_diff


def apply_scene_diff(a: Scene, js_diff: dict) -> Scene:
    """Applies a diff to a scene"""
    a_dslj = figma_to_json_dsl(a)
    a_patched_dslj = patch(a_dslj, js_diff)
    a_formatted = json_dsl_to_figma(a_patched_dslj)
    return a_formatted
