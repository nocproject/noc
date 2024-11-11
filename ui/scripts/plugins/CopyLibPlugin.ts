import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";

export class CopyLibPlugin{
  private readonly sourcePath: string;
  private readonly targetDir: string;

  constructor(sourcePath: string = "lib", targetDir: string){
    this.sourcePath = sourcePath;
    this.targetDir = targetDir;
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "copy-lib",
      setup: (build: esbuild.PluginBuild) => {
        build.onStart(() => {
          console.log("Starting to copy lib folder...");
        });

        build.onEnd(async() => {
          try{
            const targetPath = path.join(this.targetDir, "lib");
            await fs.copy(this.sourcePath, targetPath);
            console.log(`Lib folder copied successfully from ${this.sourcePath} to ${targetPath}`);
          } catch(error){
            console.error("Error copying lib folder:", error);
          }
        });
      },
    };
  }
}
