import * as esbuild from "esbuild";
import type {Options} from "espree";
import fs from "fs-extra";
import path from "path";
import {DependencyGraph} from "../DependencyGraph.ts";
import {ExtJsParser} from "../ExtJsParser.ts";
import {ExtDefineVisitor} from "../visitors/ExtDefineVisitor.ts";

interface PluginOptions {
  basePath: string;
  paths: Record<string, string>;
  entryPoint: string;
  parserOptions?: Options;
  cacheDir?: string;
  debug?: boolean;
}

export class NocLoaderPlugin{
  private readonly options: PluginOptions;
  private readonly graph = new DependencyGraph();
  private readonly excludeDir = [
    "js",
    "locale",
  ];
  private readonly excludeClasses = [
    "Ext.ux.layout.component.form.ItemSelector",
    "Ext.ux.layout.component.form.MultiSelect",
    // Handlebars is not defined
    "NOC.fm.classificationrule.templates.TestResult",
    "NOC.inv.connectiontype.templates.Test",
    "NOC.inv.objectmodel.templates.JSON",
    "NOC.inv.objectmodel.templates.Test",
    "NOC.main.prefixtable.templates.TestResultTemplate",
    "NOC.main.timepattern.templates.TestResultTemplate",
    "NOC.project.project.templates.AllocatedResources",
  ];

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
            const content = await fs.readFile(args.path, "utf8");
            for(const [namespace, dirPath] of Object.entries(this.options.paths)){
              const fullPath = path.join(this.options.basePath, dirPath);
              this.log(`Scanning directory ${fullPath} for Ext.define classes`);
              await this.scanDirectoryRecursive(fullPath, namespace);
            }
            this.excludeClasses.forEach(className => {
              this.graph.remove(className);
            });
            const imports = this.graph.topologicalSort()?.map(cl=>`import '${cl}'`).join("\n");
            return {
              contents: imports + content,
              loader: "js",
            };
          });
        build.onResolve({filter: /^(NOC\.|Ext\.ux\.)/}, args => {
          this.log("Resolving:", args.path);
          const parts = args.path.split(".");
          const filePath = path.join(
            this.options.basePath,
            this.options.paths?.NOC || "",
            ...parts.slice(1, -1),
            `${parts[parts.length - 1]}.js`,
          );
          return {path: filePath};
        });
      },
    }
  }

  private async scanDirectoryRecursive(dir: string, namespace: string): Promise<void>{
    try{
      const entries = await fs.readdir(dir, {withFileTypes: true});

      for(const entry of entries){
        const fullPath = path.join(dir, entry.name);

        if(entry.isDirectory() && !this.excludeDir.includes(entry.name)){
          await this.scanDirectoryRecursive(fullPath, namespace);
        } else if(entry.isFile() && entry.name.endsWith(".js")){
          const {isExt, contents} = await this.isExtClass(fullPath);

          if(isExt && contents){
            const visitor = new ExtDefineVisitor();
            const parser: ExtJsParser = new ExtJsParser(contents, {parserOptions: this.options.parserOptions}, visitor);
            this.log(`Found Ext class in ${fullPath}`);
            this.graph.add(parser.findDependencies());
          }
        }
      }
    } catch(error){
      this.logError(error as Error, `Scanning directory: ${dir}`);
    }
  }

  private async isExtClass(filePath: string): Promise<{ isExt: boolean; contents?: string }>{
    try{
      const contents = await fs.readFile(filePath, "utf8");
      return {
        isExt: contents.includes("Ext.define"),
        contents,
      };
    } catch(error){
      this.logError(error as Error, `Reading file: ${filePath}`);
      return {isExt: false};
    }
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
