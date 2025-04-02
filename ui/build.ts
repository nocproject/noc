import type {BuilderOptions} from "./scripts/builders/BaseBuilder.ts";
import {BaseBuilder} from "./scripts/builders/BaseBuilder.ts";
import {DevBuilder} from "./scripts/builders/DevBuilder.ts";
import {MonacoEditorBuilder} from "./scripts/builders/MonacoEditorBuilder.ts";
import {ProdBuilder} from "./scripts/builders/ProdBuilder.ts";
import {VendorBuilder} from "./scripts/builders/VendorBuilder.ts";

const mode = process.argv[2] as "prod" | "dev" | "vendor" | "vendor-dev" | "monaco" | "monaco-dev";
if(!mode || !["prod", "dev", "vendor", "vendor-dev", "monaco", "monaco-dev"].includes(mode)){
  throw new Error('Mode must be either "prod", "dev", "vendor", "vendor-dev", "monaco" or "monaco-dev"');
}

const isDev = ["dev", "vendor-dev", "monaco-dev"].includes(mode);

const commonOptions: BuilderOptions = {
  buildDir: "dist",
  entryPoint: "web/main/desktop/app.js",
  cacheDir: ".cache",
  pluginDebug: false,
  isDev,
  htmlTemplate: `scripts/index-template.html`,
  assetsDir: "assets",
  cssEntryPoints: ["scripts/app.css"],
  aliases: {
    "@cssPkg": "./pkg",
    "@cssWeb": "./web/css",
    "/ui/web/img": "./web/img",
  },
  toReplaceMethods: [
    // { // replace new_load_scripts() with the third argument of the call expression
    //   // new_load_scripts([], me, me._render); => me._render();
    //   name: "new_load_scripts",
    //   replacement: {
    //     type: "CallExpression",
    //     callee: (node: CallExpression) => node.arguments[2] as Expression,
    //     arguments: [],
    //   },
    // },
    {
      // remove console.debug() calls
      name: "console.log",
      replacement: {
        type: "UnaryExpression",
        argument: {type: "Literal", value: 0},
        operator: "void",
        prefix: true,
      },
    },
    {
      // remove console.debug() calls
      name: "console.debug",
      replacement: {
        type: "UnaryExpression",
        argument: {type: "Literal", value: 0},
        operator: "void",
        prefix: true,
      },
    },
  ],
  esbuildOptions: {
    bundle: true,
    sourcemap: isDev,
    // ToDO make option bundle suffix configurable
    // 'bundle' used in BaseBuilder.cleanBuildDir() to remove files
    // used in LoggerPlugin.checkDirectory() to exclude files from changed list
    entryNames: isDev ? "[name]-bundle" : "[name]-[hash]",
    metafile: true,
    minify: !isDev,
    keepNames: false,
    format: "esm",
  },
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    comment: false,
    tokens: false,
    range: false,
    loc: false,
  },
  generateOptions: {
    indent: "  ",
    lineEnd: "\n",
  },
};

let builder: BaseBuilder;

switch(mode){
  case "dev":
    builder = new DevBuilder({
      ...commonOptions,
    });
    break;
  case "prod":
    builder = new ProdBuilder(commonOptions);
    break;
  case "vendor":
  case "vendor-dev": {
    delete commonOptions.cssEntryPoints;
    builder = new VendorBuilder({
      ...commonOptions,
      entryPoint: `${commonOptions.cacheDir}/vendor.js`,
      esbuildOptions: {
        ...commonOptions.esbuildOptions,
        entryNames: "external-libs.js",
      },
    });
    break;
  }
  case "monaco":
  case "monaco-dev": {
    builder = new MonacoEditorBuilder({
      ...commonOptions,
      cssEntryPoints: [],
    });
    break;
  }
}

builder.start();

process.on("SIGINT", async() => {
  if(builder && "stop" in builder){
    await builder.stop();
  }
  process.exit(0);
});
