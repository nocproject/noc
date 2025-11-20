import type * as astring from "astring";
import {generate} from "astring";
import * as esbuild from "esbuild";
import * as espree from "espree";
import type {Node} from "estree";
import fs from "fs-extra";
import {SourceMapGenerator} from "source-map";
import type {MethodReplacement} from "../visitors/MethodReplaceVisitor.ts";
import {MethodReplaceVisitor} from "../visitors/MethodReplaceVisitor.ts";

interface PluginOptions {
  toReplaceMethods: MethodReplacement[] | undefined;
  parserOptions?: espree.Options;
  generateOptions?: astring.Options;
  isDev: boolean;
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
          let contents = await fs.readFile(args.path, "utf8");
          this.log(`Processed file: ${args.path}`);
          if(new RegExp(/.*theme-.*\.js$/).test(args.path)){
            contents = await this.removePolyfills(contents);
          }
          return {
            contents: this.processFile(args.path, contents, this.options.isDev),
            loader: "js",
          };
        });
      },
    };
  }

  private async removePolyfills(content: string): Promise<string>{
    // Looking for the end of polyfills by the first Ext.define
    const extDefineIndex = content.indexOf("Ext.define('Ext.theme.neptune.Component'");
    
    if(extDefineIndex === -1){
      return content;
    }
    
    return content.substring(extDefineIndex);
  }
  private processFile(fileName: string, contents: string, isDev: boolean): string{    
    let ast = espree.parse(contents, this.options.parserOptions) as Node;

    this.options.toReplaceMethods?.map((method) => {
      const visitor = new MethodReplaceVisitor(method.name, method.replacement, ast);
      ast = visitor.getResults();
    });

    if(isDev){
      const map = new SourceMapGenerator({
          file: fileName,
        }),
        generatedCode = generate(ast, {
          ...this.options.generateOptions,
          sourceMap: map,
        }),
        base64Map = Buffer.from(map.toString(), "utf8").toString("base64");

      return generatedCode +
        "\n//# sourceMappingURL=data:application/json;base64," +
        base64Map;
    } else{
      return generate(ast, this.options.generateOptions);
    }
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
