from typing import List, Dict, Union, Tuple, Optional
from typing import TypedDict

Coord = Tuple[int, int]
Scene = Union[List[Dict], Dict]  # raw figma scene
DSLJson = Union[Dict, List[Dict]]  # normalized to JSON format we input/output
DSLYaml = str
NodeType = Union['RECTANGLE', 'ELLIPSE', 'GROUP', 'FRAME']


class FigmaColor(TypedDict):
    r: float
    g: float
    b: float


class FigmaPosition(TypedDict):
    x: float
    y: float


Justification = Union['LEFT', 'CENTER', 'RIGHT', 'JUSTIFIED']


class FigmaNodeInner(TypedDict):
    color: FigmaColor
    height: float
    width: float
    position: FigmaPosition
    opacity: Optional[float]
    cornerRadius: Optional[int]
    strokeWeight: Optional[int]
    children: Optional[List['FigmaNode']]
    dropShadow: Optional[int]
    textAlignHorizontal: Optional[Justification]


class FigmaNode(TypedDict):
    name: str
    type: NodeType
    node: FigmaNodeInner


class FigmaFrameInner(TypedDict):
    children: List[FigmaNode]


class FigmaFrame(TypedDict):
    name: str
    type: str
    node: FigmaFrameInner


class DSLNodeInner(TypedDict):
    color: str
    height: int
    width: int
    position: Coord
    opacity: Optional[float]
    cornerRadius: Optional[int]
    strokeWeight: Optional[int]
    children: Optional[List['DSLNode']]
    dropShadow: Optional[int]


class DSLNode(TypedDict):
    name: str
    type: NodeType
    node: DSLNodeInner


UserTextInput = str
EditPrompt = str
PrimaryPrompt = str
