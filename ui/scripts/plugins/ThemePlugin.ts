import type {Plugin} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import type {Theme} from "../builders/BaseBuilder.ts";

interface ThemePluginOptions {
  debug: boolean;
  isDev: boolean;
  outputDir: string;
  outputFileName: string;
  theme: Theme;
}

export class ThemePlugin{
  private readonly options: ThemePluginOptions;
  
  constructor(options: ThemePluginOptions){
    this.options = options;
  }
  
  getPlugin(): Plugin{
    return {
      name: "theme-plugin",
      setup: (build) => {
        build.onStart(async() => {
          await this.generateThemeFiles();
        });
        
        // build.onLoad({filter: /desktop[/\\]app\.js$/}, async(args) => {
        //   const sourceContent = fs.readFileSync(args.path, "utf-8");
          
        //   return {
        //     contents: sourceContent,
        //     loader: "js",
        //   };
        // });
      },
    };
  }
  private async generateThemeFiles(): Promise<void>{
    try{
      const libraryFiles = [
        {name: `pkg/extjs/classic/theme-${this.options.theme}/theme-${this.options.theme}.js`, format: "iife"},
      ];
      
      const projectRoot = path.resolve(process.cwd());
      const outputFile = path.join(projectRoot, this.options.outputDir, this.options.outputFileName);
      
      this.log(`Generating theme files: ${outputFile}`);
      
      let combinedLibraries = "// Combined theme for NOC\n";
      combinedLibraries += "// Generated: " + new Date().toISOString() + "\n\n";
      for(const libPath of libraryFiles){
        try{
          const filePath = path.join(projectRoot, libPath.name);
          
          if(fs.existsSync(filePath)){
            const content = fs.readFileSync(filePath, "utf-8");
            if(libPath.format === "iife") combinedLibraries += "(function() {\n";
            combinedLibraries += `\n/* ${libPath} */\n${content}\n`;
            if(libPath.format === "iife") combinedLibraries += "\n})();\n";
          } else{
            console.warn(`Warning: File not found: ${filePath}`);
          }
        } catch(error){
          this.logError(error as Error, `Error reading library file ${libPath}:`);
        }
      }
      if(!fs.existsSync(path.dirname(outputFile))){
        fs.mkdirSync(path.dirname(outputFile), {recursive: true});
      }
      
      fs.writeFileSync(outputFile, combinedLibraries);
      
      this.log(`Theme files generated successfully: ${outputFile}`);
    } catch(error){
      this.logError(error as Error, "Failed to generate theme files");
    }
  }
  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[ThemePlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[ThemePlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}