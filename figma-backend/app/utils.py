import yaml
from copy import deepcopy
from jsondiff import diff
from typing import List, Tuple
from app.types import Coord, Scene, FigmaNode, FigmaFrame

OUTPUT_WIDTH = 100.0


def coord_minmax(tlbrs: List[Tuple[Coord, Coord]]):
    tls = [x[0] for x in tlbrs]
    brs = [x[1] for x in tlbrs]
    return (
        (min([z[0] for z in tls]), min([z[1] for z in tls])),
        (max([z[0] for z in brs]), max([z[1] for z in brs]))
    )


def get_tlbr(x: Scene):
    if type(x) is list:
        return coord_minmax([get_tlbr(y) for y in x])
    elif x['type'] == 'FRAME':
        return coord_minmax([get_tlbr(y) for y in x['node']['children']])
    elif x['type'] == 'GROUP':
        return coord_minmax([get_tlbr(y) for y in x['node']['children']])
    else:
        pos = x['node']['position']
        tl, br = (
            (pos['x'], pos['y']),
            (pos['x'] + x['node']['width'], pos['y'] + x['node']['height'])
        )
        return tl, br


def get_tl_br_w_h(scene: Scene):
    tl, br = get_tlbr(scene)
    w = br[0] - tl[0]
    h = br[1] - tl[1]
    return tl, br, w, h


def affine_trans(scene: Scene, x=0.0, y=0.0, scale: float = 1.0):
    """translates all coords and dimensions by x_orig = (x_orig + x) * scale"""
    scene = deepcopy(scene)
    if type(scene) is list:
        return [affine_trans(node, x=x, y=y, scale=scale) for node in scene]
    elif scene.get('type') in ('FRAME', 'GROUP'):
        scene['node']['children'] = [affine_trans(child, x=x, y=y, scale=scale) for child in scene['node']['children']]
        return scene
    else:
        position = scene['node']['position']
        scene['node']['position'] = {
            'x': int((position['x'] + x) * scale),
            'y': int((position['y'] + y) * scale)
        }
        if scene['node'].get('fontSize'):
            scene['node']['fontSize'] = int(scale * scene['node']['fontSize'])
        scene['node']['width'] = int(scale * scene['node']['width'])
        scene['node']['height'] = int(scale * scene['node']['height'])
        return scene


def normalize_dims(scene):
    """Scales everything to (100, 100) and translates to (0, 0)"""
    tl, br, w, h = get_tl_br_w_h(scene)
    scale = OUTPUT_WIDTH / float(w)
    scene_ = affine_trans(scene, x=-tl[0], y=-tl[1])  # translate to (0, 0)
    scene_ = affine_trans(scene_, x=0, y=0, scale=scale)  # scale to width = 100
    return scene_


def denormalize_dims(scene: Scene, tl: Coord, w: int):
    """Scales everything back to original dimensions and translates back to original position"""
    scale = float(w) / OUTPUT_WIDTH
    scene_ = affine_trans(scene, scale=scale)
    scene_ = affine_trans(scene_, x=tl[0], y=tl[1])
    return scene_


def get_primary_and_edit_example(frame: FigmaFrame) -> Tuple[FigmaNode, FigmaNode]:
    """Returns the primary and edit example nodes from a frame"""
    examples = deepcopy(frame['node']['children'])
    if len(examples) != 2:
        raise Exception(f'Error in example frame {frame["name"]}: must have exactly 2 examples')
    examples = sorted(examples, key=lambda x: x['name'])
    return examples[0], examples[1]


def lists_to_dicts(a):
    """gets rid of lists so we can do better json diffs"""
    if type(a) is list:
        return {ix: lists_to_dicts(x) for ix, x in enumerate(a)}
    elif type(a) is dict:
        return {k: lists_to_dicts(v) for k, v in a.items()}
    else:
        return a


def dicts_to_lists(a):
    """turns dicts with all digit entries into lists"""
    if type(a) is list:  # should never happen
        return [dicts_to_lists(x) for x in a]
    elif type(a) is dict:
        if all([type(x) is int for x in a.keys()]):
            listified = [x[1] for x in sorted(list(a.items()), key=lambda x: x[0])]
            return [dicts_to_lists(x) for x in listified]
        else:
            return {k: dicts_to_lists(v) for k, v in a.items()}
    else:
        return a


def extract_children(d):
    """takes care of edge case where GPT-3 doesn't realize only groups can have children"""
    if type(d) is list:
        return [extract_children(x) for x in d]
    if type(d) is dict:
        if (d.get('type') not in ('FRAME', 'GROUP')) and d.get('node', {}).get('children'):
            # print(d)
            d_ = deepcopy(d)
            children = d_.get('node', {}).get('children', [])
            children = [extract_children(x) for x in children]
            del d_['node']['children']
            all_children = [d_, *children]
            # x, y = d['node']['position']['x'], d['node']['position']['y']
            # all_children = [affine_trans(c, x=-x, y=-y, scale=1.0) for c in all_children] # child coords are relative to parent
            return {
                'name': f'{d.get("name")} Group',
                'type': 'GROUP',
                'node': {
                    'children': all_children
                }
            }
        else:
            return {k: extract_children(v) for k, v in d.items()}
    else:
        return d


########################################################################################################################
# Conversion Utils
########################################################################################################################

from app.types import FigmaColor


def rgb_to_hex(rgb: FigmaColor) -> str:
    rgb = (int(rgb['r'] * 255), int(rgb['g'] * 255), int(rgb['b'] * 255))
    return '#%02x%02x%02x' % rgb


def hex_to_rgb(hex: str) -> FigmaColor:
    hex = hex.lstrip('#')
    hlen = len(hex)
    rgb = tuple(int(hex[i:i + hlen // 3], 16) / 255.0 for i in range(0, hlen, hlen // 3))
    return {
        'r': rgb[0],
        'g': rgb[1],
        'b': rgb[2]
    }
