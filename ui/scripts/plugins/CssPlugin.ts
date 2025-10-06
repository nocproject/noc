import type * as esbuild from "esbuild";

interface CssPluginOptions {
  entryPoints: string[];
  debug: boolean;
  isDev: boolean;
}

export class CssPlugin{
  private readonly options: CssPluginOptions;

  constructor(options: CssPluginOptions){
    this.options = options;
  }

  getPlugin(): esbuild.Plugin{
    return {
      name: "css-plugin",
      setup: (build) => {
        build.onStart(() => {
          this.log("Starting CSS processing...");
        });

        build.onEnd((result) => {
          if(result.errors.length === 0){
            this.log("CSS processing completed successfully");
          } else{
            this.logError(new Error(
              result.errors.map(
                (err) => `${err.text} (${err.location?.file}:${err.location?.line})`)
                .join("\n"),
            ), "CSS processing");
          }
        });
      },
    };
  }

  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[CssPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[CssPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}
