import yaml
import pickle
from copy import deepcopy
from app.utils import normalize_dims, get_primary_and_edit_example
from app.conversion import figma_to_yaml, yaml_to_figma, get_scene_diff
from app.types import Scene, FigmaFrame
from app.types import UserTextInput, EditPrompt, PrimaryPrompt


########################################################################################################################
# Primary Prompt Construction
########################################################################################################################

def get_frame_primary_prompt(frame: FigmaFrame):
    """Returns a primary prompt from a frame - that is, a prompt of just creating the thing"""
    ex_primary, _ = get_primary_and_edit_example(frame)
    ex_prompt = ex_primary['name'].split('.')[1].strip()
    ex_yaml = figma_to_yaml(ex_primary)
    return f"""{ex_prompt}\n```\n{ex_yaml}```\n---\n"""


def get_primary_prompt(scene: Scene):
    """Deals purely with creation of new objects"""
    primary_prompts = [get_frame_primary_prompt(frame) for frame in scene]
    return '\n'.join(primary_prompts)


########################################################################################################################
# Edit Prompt Construction
########################################################################################################################


def get_frame_edit_prompt(frame: FigmaFrame) -> EditPrompt:
    """Takes a single example of an edit and makes a prompt entry for it"""
    # =====[ Extract the examples ]=====
    ex_before, ex_after = get_primary_and_edit_example(frame)

    # =====[ Get prompt & set their names ]=====
    mod_prompt = ex_after['name'].split('.')[1].strip()
    ex_before['name'] = 'Input'
    ex_after['name'] = 'Input'

    # =====[ Dump them to YAML ]=====
    ex_before_yaml = figma_to_yaml(ex_before)
    js_diff = get_scene_diff(ex_before, ex_after)
    diff_yaml = yaml.dump(js_diff, sort_keys=False)
    return f"""Input:
```
{ex_before_yaml}
```

Modification: {mod_prompt}
```
{diff_yaml}
```
---
"""


def get_edit_prompt(scene):
    filtered_scene = [x for x in scene if not '(Primary Only)' in x['name']]
    edit_prompts = [get_frame_edit_prompt(frame) for frame in filtered_scene]
    return '\n'.join(edit_prompts)


def get_live_edit_prompt(prompt: UserTextInput, scene: Scene) -> EditPrompt:
    scene_yaml = figma_to_yaml(scene)
    return f"""Input: 
```
{scene_yaml}
```
Modification: {prompt}
```"""


class QueryCreator(object):
    """Manages creation of queries for submissions to GPT-3"""
    training_scene: Scene
    primary_prefix: str
    edit_prefix: str
    DATA_PATH = '/Users/jonhack/CS/AI/text-to-figma/figma-backend/app/data.pkl'

    def __init__(self):
        pass

    def set_prefixes(self, scene: Scene):
        self.training_scene = deepcopy(scene)
        self.primary_prefix = get_primary_prompt(scene)
        self.edit_prefix = get_edit_prompt(scene)
        f = open(self.DATA_PATH, 'wb')
        pickle.dump({
            'scene': scene,
            'primary_prefix': self.primary_prefix,
            'edit_prefix': self.edit_prefix,
        }, f)

    def format_query_primary(self, prompt: UserTextInput) -> PrimaryPrompt:
        return f"""{self.primary_prefix}\n{prompt}\n```"""

    def format_query_edit(self, prompt: UserTextInput, scene: Scene) -> EditPrompt:
        midfix = get_live_edit_prompt(prompt, scene)
        return f"""{self.edit_prefix}\n{midfix}"""
