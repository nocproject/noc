import type * as esbuild from "esbuild";
import path from "path";

export interface AliasPluginOptions {
  aliases: Record<string, string>;
  debug?: boolean;
}

export class AliasPlugin{
  private readonly options: AliasPluginOptions;

  constructor(options: AliasPluginOptions){
    this.options = options;
  }

  getPlugin(): esbuild.Plugin{
    const aliases = this.options.aliases;
    const basePath = process.cwd();

    return {
      name: "alias-plugin",
      setup: (build) => {
        build.onResolve({filter: /.*/}, (args) => {
          const aliasPath = args.path;

          for(const [alias, target] of Object.entries(aliases)){
            if(aliasPath.startsWith(alias)){
              const resolvedPath = aliasPath.replace(alias, target);
              const fullResolvedPath = resolvedPath.startsWith("/") 
                ? resolvedPath 
                : path.join(basePath, resolvedPath);
                
              this.log(`Resolved ${aliasPath} to ${fullResolvedPath}`);
                
              return {
                path: fullResolvedPath,
                external: false,
              };
            }
          }
          return null;
        });
      },
    };
  }
  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[AliasPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[AliasPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}