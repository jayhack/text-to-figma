# text-to-figma

This repo is an open-source implementation of text-to-figma, [as showcased on Twitter](https://twitter.com/mathemagic1an/status/1589657222094934016) (with a few modifications.)

This code is presented as-is and may require some legwork to get it running on your own machine.


## Set up Frontend (Figma Plugin)

### Dependency Installation

Below are the steps to get the Figma plugin running. You can also find instructions at:

https://www.figma.com/plugin-docs/setup/

This plugin template uses Typescript and NPM, two standard tools in creating JavaScript applications.

First, download Node.js which comes with NPM. This will allow you to install TypeScript and other
libraries. You can find the download link here:

  https://nodejs.org/en/download/

Next, install TypeScript using the command:

```
~$: npm install -g typescript
```

Finally, in the directory of your plugin, get the latest type definitions for the plugin API by running:

```
~$: npm install --save-dev @figma/plugin-typings
```

### Running the Server

Then run VSCode with a dev server for TS:
- Open VScode
- shift + cmd + B => select `tsc: watch - tsconfig.json`

Now any time you save, the code will be updated.

Now, in Figma, run the plugin by going to plugins > development > `text-to-figma`


## Set up Backend

### Installation & Development
- edit [gpt3.py](https://github.com/jayhack/text-to-figma/blob/main/figma-backend/app/gpt3.py) to include your OpenAI key
- run [gpt3.py](https://github.com/jayhack/text-to-figma/blob/main/figma-backend/app/gpt3.py) to install dependencies
- run `source venv/bin/acivate` to activate 


### Deployment 

The backend comes with a Dockerfile and was originally deployed on fly.dev.

To deploy on fly:
- Rename `figma-backend/fly.toml.template` => `figma-backend/fly.toml`
- Run `fly launch`

