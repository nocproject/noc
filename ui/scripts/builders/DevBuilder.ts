import type {ServeResult} from "esbuild";
import * as esbuild from "esbuild";
import {LanguagePlugin} from "../plugins/LanguagePlugin.ts";
import {ReplaceMethodsPlugin} from "../plugins/ReplaceMethodsPlugin.ts";
import {BaseBuilder} from "./BaseBuilder.ts";

export class DevBuilder extends BaseBuilder{
  readonly className: string = "DevBuilder";

  async start(): Promise<void>{
    try{
      await this.initialize();
      await this.createContext();
      await this.watch();

      // const {host, port} = await this.serve();
      console.log("watching...");
      // console.log(`serve on http://${host}:${port}`);
    } catch(error){
      console.error("Development server start failed:", error);
      await this.stop();
      process.exit(1);
    }
  }

  async clean(): Promise<void>{
    await this.clearBuildDir();
  }
  
  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
    console.log("Dev builder stopped");
  }

  private async createContext(): Promise<void>{
    const options = this.getBaseBuildOptions();
    this.context = await esbuild.context({
      ...options,
      entryPoints: [
        ...(Array.isArray(options.entryPoints) ? options.entryPoints : []),
        "locale-en",
        // `${this.options.cacheDir}/locale-en.js`,
      ],
      plugins: [
        ...(options.plugins || []),
        new LanguagePlugin({
          debug: this.options.pluginDebug,
          isDev: true,
          outputDir: this.options.buildDir,
          languages: ["en"],
          cacheDir: this.options.cacheDir,
        }).getPlugin(),
        new ReplaceMethodsPlugin({
          toReplaceMethods: [
            {
              name: "NOC.core.ResourceLoader.loadSet",
              replacement: {
                type: "ExpressionStatement",
                expression: {
                  type: "CallExpression",
                  callee: {
                    type: "MemberExpression",
                    object: {
                      type: "CallExpression",
                      callee: {
                        type: "MemberExpression",
                        object: {type: "Identifier", name: "leafletAPI"},
                        property: {type: "Identifier", name: "preload"},
                        computed: false,
                        optional: false,
                      },
                      arguments: [],
                      optional: false,
                    },
                    property: {type: "Identifier", name: "then"},
                    computed: false,
                    optional: false,
                  },
                  arguments: [
                    {
                      type: "ArrowFunctionExpression",
                      params: [],
                      body: {
                        type: "CallExpression",
                        callee: {
                          type: "MemberExpression",
                          object: {type: "ThisExpression"},
                          property: {type: "Identifier", name: "createMap"},
                          computed: false,
                          optional: false,
                        },
                        arguments: [
                          {type: "Identifier", name: "data"},
                        ],
                        optional: false,
                      },
                      generator: false,
                      expression: true,
                      async: false,
                    },
                  ],
                  optional: false,
                },
              },
            },
          ],
          debug: this.options.pluginDebug,
          parserOptions: this.options.parserOptions,
          generateOptions: this.options.generateOptions,
        }).getPlugin(),
      ],
    });
  }

  private async watch(): Promise<void>{
    if(!this.context){
      throw new Error("Context not initialized");
    }
    await this.context.watch();
  }

  private async serve(): Promise<ServeResult>{
    if(!this.context){
      throw new Error("Context not initialized");
    }
    return await this.context.serve({
      servedir: this.options.buildDir,
    });
  }
}
