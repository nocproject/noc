import type * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";

export interface ImageCheckPluginOptions {
  debug?: boolean;
}

export class ImageCheckPlugin{
  private readonly emptyGifPath: string;
  private readonly basePath: string;
  private readonly options: ImageCheckPluginOptions;

  constructor(options: ImageCheckPluginOptions){
    this.basePath = process.cwd();
    this.emptyGifPath = path.join(this.basePath, "scripts/assets/empty.gif");
    this.options = options;
    this.ensureEmptyGifExists();
  }
  
  getPlugin(): esbuild.Plugin{
    return {
      name: "image-check-plugin",
      setup: (build) => {
        build.onResolve({filter: /\.(gif|png|jpe?g|svg|webp|ico)$/}, async(args) => {
          const resolvedPath = path.resolve(args.resolveDir, args.path);
          
          try{
            await fs.access(resolvedPath);
            return null;
          } catch(error){
            this.log(`${(error as Error).message}, replacing with empty.gif`);
            return {
              path: this.emptyGifPath,
              external: false,
            };
          }
        });
      },
    };
  }
  
  private async ensureEmptyGifExists(): Promise<void>{
    try{
      await fs.access(this.emptyGifPath);
    } catch(error){
      this.log((error as Error).message);
      await fs.ensureDir(path.dirname(this.emptyGifPath));
      const emptyGifBase64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
      await fs.writeFile(this.emptyGifPath, Buffer.from(emptyGifBase64, "base64"));
      
      this.log(`Created empty.gif at ${this.emptyGifPath}`);
    }
  }
    
  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[ImageCheckPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[ImageCheckPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}