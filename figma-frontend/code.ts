const getImage = async (url: string) => {
  const response = await fetch(url);
  const buffer = await response.arrayBuffer();
  const data = new Uint8Array(buffer);
  return figma.createImage(data);
};

type Color = {
  r: number;
  g: number;
  b: number;
};

type Position = {
  x: number;
  y: number;
};

type Shadow = {
  color: Color;
  x: number;
  y: number;
};

type Rectangle = {
  strokeWeight?: number;
  position: Position;
  color: Color;
  opacity?: number;
  width: number;
  height: number;
  cornerRadius?: number;
  dropShadow?: number;
};

type Text = {
  color: Color;
  fontSize: number;
  fontWeight: number;
  fontName: FontName;
  position: Position;
  width: number;
  height: number;
  characters: string;
  strokeWeight: number;
  textAlignHorizontal: "LEFT" | "CENTER" | "RIGHT" | "JUSTIFIED";
};

// Circle - x, y and radius
type Ellipse = {
  position: Position;
  color: Color;
  height: number;
  width: number;
};

type Group = {
  children: Node[];
};

type Frame = {
  children: Node[];
};

type Node = {
  name: string;
  type: "FRAME" | "GROUP" | "RECTANGLE" | "TEXT" | "ELLIPSE";
  node: Frame | Group | Ellipse | Text | Rectangle;
};

type Scene = Array<Node>;

/* ####################################################################################################
 * # Node Creation
 * #################################################################################################### */

const clone = (x: object | Array<any>): Array<any> => {
  return JSON.parse(JSON.stringify(x));
};

const createRectangle = (
  name: string,
  spec: Rectangle,
): SceneNode => {
  const node = figma.createRectangle();
  node.name = name;
  node.x = spec.position.x;
  node.y = spec.position.y;
  node.resize(spec.width, spec.height);
  // Colors
  const fills = clone(node.fills as Array<any>);
  fills[0].color = spec.color;
  node.fills = fills;
  node.strokeWeight = node.strokeWeight;
  node.cornerRadius = spec.cornerRadius;
  if (spec.dropShadow) {
    node.effects = [
      {
        type: "DROP_SHADOW",
        color: {
          r: 0,
          g: 0,
          b: 0,
          a: 0.25,
        },
        offset: {
          x: 0,
          y: spec.dropShadow,
        },
        radius: 4,
        spread: 0,
        visible: true,
        blendMode: "NORMAL",
        showShadowBehindNode: false,
      },
    ];
  }
  return node;
};

const createCircle = (name: string, spec: Ellipse): SceneNode => {
  const node = figma.createEllipse();
  node.name = name;
  node.x = spec.position.x;
  node.y = spec.position.y;
  const fills = clone(node.fills as Array<any>);
  fills[0].color = spec.color;
  node.fills = fills;
  node.resize(spec.width, spec.height);
  node.strokeWeight = node.strokeWeight;
  return node;
};

const createText = (name: string, spec: Text): SceneNode => {
  const node = figma.createText();
  node.name = name;
  node.x = spec.position.x;
  node.y = spec.position.y;
  node.resize(spec.width, spec.height);
  node.characters = spec.characters;
  node.fontSize = spec.fontSize;
  // node.fontName = spec.fontName;
  node.strokeWeight = node.strokeWeight;
  const fills = clone(node.fills as Array<any>);
  fills[0].color = spec.color;
  node.fills = fills;
  node.textAlignHorizontal = spec.textAlignHorizontal;
  return node;
};

const createGroupNode = (
  name: string,
  spec: Group,
  frame: FrameNode
): SceneNode => {
  const node = figma.group(
    spec.children.map((x) => createNode(x, frame)),
    frame
  );
  node.name = name;
  return node;
};

const createNode = (node: Node, frame: FrameNode): SceneNode => {
  if (node.type === "GROUP")
    return createGroupNode(node.name, node.node as Group, frame);
  if (node.type === "RECTANGLE")
    return createRectangle(node.name, node.node as Rectangle);
  if (node.type === "ELLIPSE")
    return createCircle(node.name, node.node as Ellipse);
  if (node.type === "TEXT") return createText(node.name, node.node as Text);
  throw new Error(`Unknown node type: ${node.type}`);
};

const createScene = (scene: Scene, frame: FrameNode): SceneNode => {
  const nodes = scene.map((x) => createNode(x, frame);
  let outputGroup: GroupNode;
  if (nodes.length == 1) {
    outputGroup = nodes[0] as GroupNode;
    outputGroup.x = 0;
    outputGroup.y = 0;
  } else {
    outputGroup = figma.group(nodes, frame);
  }
  return outputGroup;
};

/* ####################################################################################################
 * # SERIALIZATION
 * #################################################################################################### */

const fill = {
  type: "SOLID",
  visible: true,
  opacity: 1,
  blendMode: "NORMAL",
  color: {
    r: 0.8509804010391235,
    g: 0.8509804010391235,
    b: 0.8509804010391235,
  },
};

const serializeRectangleNode = (node: RectangleNode): Node => {
  const fills = node.fills[0].color;
  const opacity = node.fills[0].opacity;
  let dropShadow;
  if (node.effects.length > 0 && node.effects[0].type === "DROP_SHADOW") {
    dropShadow = node.effects[0].offset.y;
  }
  return {
    name: node.name,
    type: "RECTANGLE",
    node: {
      color: fills,
      opacity: opacity,
      position: {
        x: node.x,
        y: node.y,
      },
      cornerRadius: node.cornerRadius as number,
      width: node.width,
      height: node.height,
      strokeWeight: node.strokeWeight,
      dropShadow: dropShadow,
    },
  };
};

const serializeTextNode = (node: TextNode): Node => {
  return {
    name: node.name,
    type: "TEXT",
    node: {
      characters: node.characters,
      color: node.fills[0].color,
      fontSize: node.fontSize,
      fontWeight: node.fontWeight,
      // fontName: node.fontName,
      position: {
        x: node.x,
        y: node.y,
      },
      width: node.width,
      height: node.height,
      textAlignHorizontal: node.textAlignHorizontal,
    },
  };
};

const serializeEllipseNode = (node: EllipseNode): Node => {
  return {
    name: node.name,
    type: "ELLIPSE",
    node: {
      position: {
        x: node.x,
        y: node.y,
      },
      color: node.fills[0].color,
      height: node.height,
      width: node.width,
    },
  };
};

const serializeNode = (node: SceneNode): Node => {
  if (node.type === "RECTANGLE") return serializeRectangleNode(node);
  else if (node.type === "TEXT") return serializeTextNode(node);
  else if (node.type === "ELLIPSE") return serializeEllipseNode(node);
  else if (node.type === "GROUP") return serializeGroupNode(node);
  else if (node.type === "FRAME") return serializeFrameNode(node);
  else throw new Error(`Unknown node type: ${node.type}`);
};

const serializeGroupNode = (node: GroupNode): Node => {
  const children = node.children.map((x) => serializeNode(x));
  return {
    name: node.name,
    type: "GROUP",
    node: {
      children: children,
    },
  };
};

const serializeFrameNode = (node: FrameNode): Node => {
  const children = node.children.map((x) => serializeNode(x));
  return {
    name: node.name,
    type: "FRAME",
    node: {
      children: children,
    },
  };
};

/* ####################################################################################################
 * # UTILS
 * #################################################################################################### */

const serverUrl = "http://localhost:8081";

const testConnection = async () => {
  const response = await fetch(`${serverUrl}/healthcheck`, {
    method: "POST",
    headersObject: {
      "Content-Type": "application/json",
    },
  });
  const text = await response.text();
  const json = JSON.parse(text);
  if (json.status === "ok") {
    console.log("Connection to server is ok");
  } else {
    console.error("Connection to server is not ok");
  }
};

function ab2str(buf: Uint16Array) {
  return String.fromCharCode.apply(null, new Uint16Array(buf));
}

function str2ab(str: string): Uint8Array {
  var buf = new ArrayBuffer(str.length); // 2 bytes for each char
  var bufView = new Uint8Array(buf);
  for (var i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return bufView;
}

const saveScene = async () => {
  const exampleNodes = figma.currentPage.children.filter((x) =>
    x.name.startsWith("Example")
  );
  const scene = exampleNodes.map((node) => serializeNode(node));
  const response = await fetch(`${serverUrl}/save-scene`, {
    method: "POST",
    headersObject: { "Content-Type": "application/json" },
    body: str2ab(JSON.stringify({ scene })),
  });
  const text = await response.text();
  const json = JSON.parse(text);
  console.log("saveScene Success", { json });
};

type TaskType = "primary" | "edit";

const runPrompt = async (task: TaskType, data: object) => {
  const endpoint = {
    primary: "/convert/primary",
    edit: "/convert/edit",
  }[task];
  const response = await fetch(`${serverUrl}${endpoint}`, {
    method: "POST",
    headersObject: { "Content-Type": "application/json" },
    body: str2ab(JSON.stringify(data)),
  });
  const text = await response.text();
  const json = JSON.parse(text);
  console.log("runPrompt success", { json });
  return json;
};

/* ####################################################################################################
 * # MAIN
 * #################################################################################################### */

const getCurrentSelection = (): Array<SceneNode> => {
  return figma.currentPage.selection.filter((node) => node.type !== "FRAME");
};

const getFrame = (): FrameNode => {
  return figma.currentPage.children.filter((x) =>
    x.name.startsWith("Primary")
  )[0] as FrameNode;
};

const signalComplete = () => {
  figma.ui.postMessage({ type: "loading-complete" });
};

const createImage = async (url: string) => {};

async function main() {
  //=====[ Boot ]=====
  figma.showUI(__html__, { height: 214, width: 400 });
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await testConnection();
  await saveScene();

  // Calls to "parent.postMessage" from within the HTML page will trigger this
  // callback. The callback will be passed the "pluginMessage" property of the
  // posted message.
  figma.ui.onmessage = async (msg) => {
    console.log("Message");
    if (msg.type === "submit-prompt") {
      const { prompt } = msg;
      const selection = getCurrentSelection();
      const frame = getFrame();
      const task = selection.length === 0 ? "primary" : "edit";
      const scene = selection.map((node) => serializeNode(node));
      console.log(`Running task: ${task}`);
      const { outputScene, x, y } = await runPrompt(task, { prompt, scene });
      const outputGroup = createScene(outputScene, frame);
      if (task === "primary") {
        outputGroup.x = 400;
        outputGroup.y = 400;
      } else {
        outputGroup.x = x;
        outputGroup.y = y;
        selection.map((x) => x.remove());
      }
      signalComplete();
      figma.currentPage.selection = [outputGroup];
      figma.viewport.scrollAndZoomIntoView([outputGroup]);
    }

    // Make sure to close the plugin when you're done. Otherwise the plugin will
    // keep running, which shows the cancel button at the bottom of the screen.
    // figma.closePlugin();
  };
}

main();
