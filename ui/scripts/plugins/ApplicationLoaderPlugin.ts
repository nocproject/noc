import * as esbuild from "esbuild";
import type {Options} from "espree";
import fs from "fs-extra";
import path from "path";
import {DependencyGraph} from "../DependencyGraph.ts";
import {ExtJsParser} from "../ExtJsParser.ts";
import {ExtApplicationVisitor} from "../visitors/ExtApplicationVisitor.ts";
import {ExtDefineVisitor} from "../visitors/ExtDefineVisitor.ts";

interface PluginOptions {
  basePath: string;
  paths: Record<string, string>;
  entryPoint: string;
  parserOptions?: Options;
  cacheDir?: string;
  debug?: boolean;
}

export class ApplicationLoaderPlugin{
  private readonly options: PluginOptions;
  private readonly graph = new DependencyGraph();

  constructor(options: PluginOptions){
    this.options = options;
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "noc-loader-plugin",
      setup: (build) => {
        // build.onStart(async() => {
        // this.log("NocLoaderPlugin started");
        // });
        build.onLoad(
          {filter: new RegExp(this.options.entryPoint)},
          async(args) => {
            this.log(`Scanning application ${args.path}`);
            const content = await fs.readFile(args.path, "utf8");
            const visitor = new ExtApplicationVisitor();
            const parser: ExtJsParser = new ExtJsParser(content, {parserOptions: this.options.parserOptions}, visitor);
            const dependencies = parser.findDependencies();

            await this.addDependencies(dependencies.requires);
            const imports = this.graph.topologicalSort()?.map(className=>`import '${className}'`).join("\n");
            return {
              contents: imports + "\n" + content,
              loader: "js",
            };
          });
        build.onResolve({filter: /^(NOC\.|Ext\.ux\.)/}, args => {
          this.log("Resolving:", args.path);
          const filePath = this.getFilePath(args.path);
          this.log("       to:", filePath);
          if(fs.existsSync(filePath)){
            return {path: filePath};
          }
          this.logError(
            new Error(`File ${filePath} not found for ${args.path}`),
            "ApplicationLoaderPlugin: onResolve");
        });
      },
    }
  }

  private async addDependencies(dependencies: string[]): Promise<void>{
    for(const dep of dependencies){
      this.log(dep);
      const filePath = this.getFilePath(dep);
      if(fs.existsSync(filePath)){
        const content = await fs.readFile(filePath, "utf8");
        const visitor = new ExtDefineVisitor();
        const parser: ExtJsParser = new ExtJsParser(content, {parserOptions: this.options.parserOptions}, visitor);
        const dependencies = parser.findDependencies();
        this.graph.add(dependencies);
        if(dependencies.requires.length > 0){
          this.addDependencies(dependencies.requires);
        }
      }
      this.log("       to:", filePath);
    }
  }

  private getFilePath(pathString: string): string{
    const parts = pathString.split(".");
    let resultPath: string = "";

    if(this.options.paths){
      Object.entries(this.options.paths).forEach(([key, value]) => {
        if(parts[0] === key){
          resultPath = path.join(this.options.basePath, value, ...parts.slice(1, -1), `${parts[parts.length - 1]}.js`);
        }
      });
    }
    return resultPath;
  }

  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[NocLoaderPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[NocLoaderPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}
