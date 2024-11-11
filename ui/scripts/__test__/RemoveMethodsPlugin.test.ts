import * as esbuild from "esbuild";
import type {CallExpression, Expression} from "estree";
import * as fs from "fs-extra";
import * as path from "path";
import {ReplaceMethodsPlugin} from "../plugins/ReplaceMethodsPlugin.ts";

describe("ReplaceMethodsPlugin", () => {
  const testDir = path.join(__dirname, "test-temp");

  beforeEach(async() => {
    await fs.ensureDir(testDir);
  });

  afterEach(async() => {
    await fs.remove(testDir);
  });

  it("should remove specified methods from JavaScript code", async() => {
    const inputCode = `
        console.debug("NOC.core.StateProvider");
        Ext.define("NOC.core.StateProvider", {
          extend: "Ext.state.Provider",
          url: "/main/desktop/state/",
          constructor: function(config2) {
            var me2 = this;
            me2.callParent();
            me2.state = me2.loadPreferences();
            console.log("User preferences state: ", me2.state);
          }
        });
    `;

    const inputFile = path.join(testDir, "input.js");
    await fs.writeFile(inputFile, inputCode);

    const plugin = new ReplaceMethodsPlugin({
      toReplaceMethods: [
        {
          name: "console.debug",
          replacement: {
            type: "UnaryExpression",
            argument: {type: "Literal", value: 0},
            operator: "void",
            prefix: true,
          },
        },
        {
          name: "console.log",
          replacement: {
            type: "UnaryExpression",
            argument: {type: "Literal", value: 0},
            operator: "void",
            prefix: true,
          },
        },
      ],
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
      },
    });

    const result = await esbuild.build({
      entryPoints: [inputFile],
      bundle: false,
      write: false,
      plugins: [plugin.getPlugin()],
    });

    const outputCode = result.outputFiles[0].text;

    expect(outputCode).not.toContain("console.debug");
    expect(outputCode).not.toContain("console.log");
  });

  it("should handle replace method new_load_scripts", async() => {
    const inputCode = `
      console.debug("Defining NOC.inv.channel.Application");
      Ext.define("NOC.inv.channel.Application", {
        extend: "NOC.core.ModelApplication",
        requires: [
          "NOC.project.project.LookupField",
          "NOC.crm.subscriber.LookupField",
          "NOC.crm.supplier.LookupField",
          "NOC.main.remotesystem.LookupField",
          "Ext.ux.form.GridField",
        ],
        model: "NOC.inv.channel.Model",
        search: true,
        renderScheme: function(data){
          var me = this;
          if(typeof Viz === "undefined"){
            new_load_scripts([
              "/ui/pkg/viz-js/viz-standalone.js",
            ], me, Ext.bind(me._render, me, [data]));
          } else{
            me._render(data);
          }
        },
      });
    `;

    const inputFile = path.join(testDir, "input.js");
    await fs.writeFile(inputFile, inputCode);

    const plugin = new ReplaceMethodsPlugin({
      toReplaceMethods: [
        {
          name: "new_load_scripts",
          replacement: {
            type: "CallExpression",
            callee: (node: CallExpression) => node.arguments[2] as Expression,
            arguments: [],
          },
        },
        {
          name: "console.debug",
          replacement: {
            type: "UnaryExpression",
            argument: {type: "Literal", value: 0},
            operator: "void",
            prefix: true,
          },
        },
      ],
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
      },
    });

    const result = await esbuild.build({
      entryPoints: [inputFile],
      bundle: false,
      write: false,
      plugins: [plugin.getPlugin()],
    });

    const outputCode = result.outputFiles[0].text;
    expect(outputCode).not.toContain("console.debug");
    expect(outputCode).not.toContain("new_load_scripts");
  });

  it("should handle files with no methods", async() => {
    const inputCode = `
      const x = 1;
      const y = 2;
      console.log(x + y);
    `;

    const inputFile = path.join(testDir, "input.js");
    await fs.writeFile(inputFile, inputCode);

    const plugin = new ReplaceMethodsPlugin({
      toReplaceMethods: [
        {
          name: "console.debug",
          replacement: {
            type: "UnaryExpression",
            argument: {type: "Literal", value: 0},
            operator: "void",
            prefix: true,
          },
        },
      ],
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
      },
    });

    const result = await esbuild.build({
      entryPoints: [inputFile],
      bundle: false,
      write: false,
      plugins: [plugin.getPlugin()],
    });

    const outputCode = result.outputFiles[0].text;
    expect(outputCode).toContain("const x = 1");
    expect(outputCode).toContain("const y = 2");
  });
});
