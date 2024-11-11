import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";
import {ExtJsDependency} from "../ExtJsDependency.ts";

interface ExtJsPluginOptions {
    basePath: string;
    paths?: Record<string, string>;
}

export class ExtJsPlugin{
  private readonly options: ExtJsPluginOptions;
  private readonly extJsDependency: ExtJsDependency;

  constructor(options: ExtJsPluginOptions){
    this.options = options;
    this.extJsDependency = new ExtJsDependency();
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "extjs-resolver",
      setup: (build: esbuild.PluginBuild) => {
        build.onLoad({filter: /\.js$/}, async(args) => {
          let contents = await fs.readFile(args.path, "utf8");
          console.log("Processing file:", args.path);
          const requires = this.extJsDependency.findDependencies(contents);

          if(requires.length > 0){
            console.log("Found dependencies:",
                        requires.map(r => ({
                          className: r.className,
                          hasCallback: r.hasCallback,
                        })),
            );
            contents = this.extJsDependency.generateCode(contents, requires);
          }

          return {
            contents,
            loader: "js",
          };
        });

        build.onResolve({filter: /^NOC\./}, args => {
          console.log("Resolving:", args.path);
          const parts = args.path.split(".");
          const filePath = path.join(
            this.options.basePath,
            this.options.paths?.NOC || "",
            ...parts.slice(1, -1),
            `${parts[parts.length - 1]}.js`,
          );
          console.warn("Resolved path:", filePath);
          return {path: filePath};
        });
      },
    };
  }
}
