import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";

export interface CopyLibPluginOptions {
  sourcePath?: string;
  targetDir: string;
  isDev?: boolean;
  debug?: boolean;
}

export class CopyLibPlugin{
  private readonly options: CopyLibPluginOptions;
  private hasInitialCopy: boolean = false;

  constructor(options: CopyLibPluginOptions){
    this.options = {
      sourcePath: "lib",
      isDev: false,
      debug: false,
      ...options,
    };
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "copy-lib",
      setup: (build: esbuild.PluginBuild) => {
        build.onStart(() => {
          if(!this.options.isDev || !this.hasInitialCopy){
            this.log("Starting to copy lib folder...");
          }
        });

        build.onEnd(async() => {
          if(!this.options.isDev || !this.hasInitialCopy){
            try{
              const targetPath = path.join(this.options.targetDir, "lib");
              await fs.copy(this.options.sourcePath!, targetPath);
              this.log(`Lib folder copied successfully from ${this.options.sourcePath} to ${targetPath}`);
              this.hasInitialCopy = true;
            } catch(error){
              this.logError(error as Error, "copying lib folder");
            }
          }
        });
      },
    };
  }

  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[CopyLibPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[CopyLibPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}
