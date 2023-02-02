import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.format_query import QueryCreator
from pydantic import BaseModel
from typing import List, Dict
import yaml
from app.utils import get_tl_br_w_h, denormalize_dims
from app.conversion import apply_scene_diff
from app.types import Scene, UserTextInput
from app.gpt3 import GPT3
from app.conversion import figma_to_yaml, yaml_to_figma

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/healthcheck')
async def healthcheck():
    return {'status': 'ok'}


########################################################################################################################
# SAVING SCENE & TRAINING DATA
########################################################################################################################

query_creator = QueryCreator()


class SaveSceneRequest(BaseModel):
    scene: Scene


@app.post('/save-scene')
async def save_scene(request: SaveSceneRequest):
    """
    Saves scene and associated edits to file;
    Should eventually migrate this to storing in a DB somewhere.
    Can also make this stateful
    """
    scene = request.scene
    query_creator.set_prefixes(scene)  # TODO: integreate DB
    return {
        'scene': scene,
        'primary_prompt_prefix': query_creator.primary_prefix,
        'edit_prompt_prefix': query_creator.edit_prefix
    }


########################################################################################################################
# Primary Query
########################################################################################################################



class PrimaryQuery(BaseModel):
    prompt: UserTextInput


@app.post('/convert/primary')
async def convert_primary(request: PrimaryQuery):
    # if True:
    #     return {'outputScene': example_data}
    print(f'[CONVERT PRIMARY] Request received: {request.prompt}')
    primary_prompt = query_creator.format_query_primary(request.prompt)
    yaml_str = GPT3.generate_yaml(primary_prompt)
    output_scene = yaml_to_figma(yaml_str, (200, 200), 400)
    return {
        'outputScene': output_scene,
    }


########################################################################################################################
# Edits
########################################################################################################################

class EditQuery(BaseModel):
    prompt: UserTextInput
    scene: List[Dict]


@app.post('/convert/edit')
async def convert_edit(request: EditQuery):
    prompt, scene = request.prompt, request.scene
    print(f'[CONVERT EDIT] Request received: {request.prompt}')
    if type(scene) is list:
        scene = scene[0]
    tl, br, w, h = get_tl_br_w_h(scene)
    edit_prompt = query_creator.format_query_edit(request.prompt, scene)
    yaml_str = GPT3.generate_yaml(edit_prompt)
    js_diff = yaml.safe_load(yaml_str)
    scene_diffed = apply_scene_diff(scene, js_diff)
    scene_diffed = denormalize_dims(scene_diffed, tl, w)
    return {
        'outputScene': [scene_diffed],
        'x': tl[0],
        'y': tl[1]
    }


if __name__ == "__main__":
    uvicorn.run('app.main:app', host="0.0.0.0", port=8081, reload=True, workers=1)
