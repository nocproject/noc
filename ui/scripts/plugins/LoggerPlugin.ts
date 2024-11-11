import * as esbuild from "esbuild";
import * as fs from "fs";
import * as path from "path";

export class LoggerPlugin{
  private readonly name = "rebuild-logger";
  private fileTimestamps: Map<string, number> = new Map();
  private isFirstBuild = true;

  getPlugin(): esbuild.Plugin{
    return {
      name: this.name,
      setup: (build: esbuild.PluginBuild) => {
        build.onStart(() => {
          const entryPoints = build.initialOptions.entryPoints as string[];
          if(!this.isFirstBuild){
            const changedFiles = this.getChangedFiles(entryPoints);
            if(changedFiles.length > 0){
              console.log("\nChanged files:");
              changedFiles.forEach(file => {
                const fullPath = path.resolve(process.cwd(), file);
                const stats = fs.statSync(fullPath);
                this.fileTimestamps.set(fullPath, stats.mtimeMs);
                console.log(stats.mtime.toISOString());
                console.log(`• ${file}`);
              });
            }
          }
          this.scanAllFiles(entryPoints);
          this.isFirstBuild = false;
        });
        build.onEnd((result) => {
          if(result.errors.length > 0){
            console.error("\nBuild failed:", result.errors);
          } else if(!this.isFirstBuild){
            console.log("\nRebuild succeeded");
          }
        });
      },
    };
  }

  private scanAllFiles(entryPoints: string[]): void{
    entryPoints.forEach(entryPoint => {
      if(typeof entryPoint === "string"){
        const rootDir = this.getRootDir(entryPoint);
        this.scanDirectory(rootDir);
      }
    });
  }

  private getRootDir(path: string): string{
    const parts = path.split("/");
    return parts.length > 1 ? parts[0] : ".";
  }

  private scanDirectory(dir: string): void{
    const files = fs.readdirSync(dir);

    files.forEach(file => {
      const fullPath = path.join(dir, file);
      const stats = fs.statSync(fullPath);

      if(stats.isDirectory()){
        this.scanDirectory(fullPath);
      } else{
        this.fileTimestamps.set(fullPath, stats.mtimeMs);
      }
    });
  }

  private getChangedFiles(entryPoints: string[]): string[]{
    const changedFiles: string[] = [];

    entryPoints.forEach(entryPoint => {
      if(typeof entryPoint === "string"){
        const rootDir = this.getRootDir(entryPoint);
        this.checkDirectory(rootDir, changedFiles, entryPoint);
      }
    });

    this.scanAllFiles(entryPoints);

    return changedFiles;
  }

  private checkDirectory(dir: string, changedFiles: string[], exclude: string): void{
    const files = fs.readdirSync(dir);

    files.forEach(file => {
      const fullPath = path.join(dir, file);
      const stats = fs.statSync(fullPath);

      if(stats.isDirectory()){
        this.checkDirectory(fullPath, changedFiles, exclude);
      } else{
        const entryBasename = path.basename(exclude).replace(path.extname(exclude), "") + "-bundle";  
        if(fullPath.includes(entryBasename)){
          return
        }
        const previousTimestamp = this.fileTimestamps.get(fullPath);
        if(!previousTimestamp || stats.mtimeMs > previousTimestamp){
          changedFiles.push(path.relative(process.cwd(), fullPath));
        }
      }
    });
  }
}
