import type * as astring from "astring";
import {generate} from "astring";
import * as esbuild from "esbuild";
import * as espree from "espree";
import type {Node} from "estree";
import fs from "fs-extra";
import type {MethodReplacement} from "../visitors/MethodReplaceVisitor.ts";
import {MethodReplaceVisitor} from "../visitors/MethodReplaceVisitor.ts";

interface PluginOptions {
  toReplaceMethods: MethodReplacement[] | undefined;
  parserOptions?: espree.Options;
  generateOptions?: astring.Options;
  debug?: boolean;
}

export class ReplaceMethodsPlugin{
  private readonly options: PluginOptions;

  constructor(options: PluginOptions){
    this.options = {
      debug: false,
      ...options,
    };
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "remove-methods-plugin",
      setup: (build) => {
        build.onLoad({filter: /\.js$/}, async(args) => {
          const contents = await fs.readFile(args.path, "utf8");
          this.log(`Processed file: ${args.path}`);
          return await this.processFile(contents);
        });
      },
    };
  }

  private async processFile(contents: string): Promise<esbuild.OnLoadResult>{
    let ast = espree.parse(contents, this.options.parserOptions) as Node;

    this.options.toReplaceMethods?.map((methodName) => {
      const visitor = new MethodReplaceVisitor(methodName.name, methodName.replacement, ast);
      ast = visitor.getResults();
    });

    const cleanedCode = generate(ast, this.options.generateOptions);

    return {
      contents: cleanedCode,
      loader: "js",
    };
  }

  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[RemoveMethodsPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[RemoveMethodsPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}
