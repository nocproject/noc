import type {Plugin} from "esbuild";
import * as fs from "fs";
import * as path from "path";

interface ExternalLibsPluginOptions {
  debug: boolean;
  isDev: boolean;
  outputDir: string;
  outputFileName: string;
}

export class ExternalLibsPlugin{
  private readonly options: ExternalLibsPluginOptions;
  
  constructor(options: ExternalLibsPluginOptions){
    this.options = options;
  }
  
  getPlugin(): Plugin{
    return {
      name: "external-libs-plugin",
      setup: (build) => {
        build.onStart(async() => {
          await this.generateExternalLibsFile();
        });
        
        build.onLoad({filter: /desktop[/\\]app\.js$/}, async(args) => {
          const sourceContent = fs.readFileSync(args.path, "utf-8");
          
          return {
            contents: sourceContent,
            loader: "js",
          };
        });
      },
    };
  }
  
  private async generateExternalLibsFile(): Promise<void>{
    try{
      const libraryFiles = [
        // Base libs and ExtJS
        {name: "web/js/jsloader.js", format: "iife"},
        {name: `pkg/extjs/ext-all${this.options.isDev ? "-debug" : ""}.js`, format: "native"},
        {name: "pkg/extjs/classic/theme-noc/theme-noc.js", format: "iife"},
        {name: "pkg/extjs/packages/charts/classic/charts.js", format: "iife"},
        {name: "web/locale/en/ext-locale-en.js", format: "iife"},
        {name: "pkg/jquery/jquery.min.js", format: "iife"},
        
        // JointJS
        {name: "pkg/lodash/lodash.min.js", format: "iife"},
        {name: "pkg/backbone/backbone.min.js", format: "iife"},
        {name: "pkg/dagre/dagre.min.js", format: "iife"},
        {name: "pkg/graphlib/graphlib.min.js", format: "iife"},
        {name: "pkg/joint/joint.min.js", format: "iife"},
        {name: "pkg/joint.layout.directedgraph/joint.layout.directedgraph.min.js", format: "iife"},
        {name: "web/wf/workflow/js/joint.element.Tools.js", format: "iife"},
      
        // Other libraries
        {name: "pkg/moment/moment.min.js", format: "iife"},
        {name: "pkg/moment-timezone/moment-timezone-with-data-1970-2030.min.js", format: "iife"},
        {name: "pkg/viz-js/viz-standalone.js", format: "iife"},
        
        // NOC modules
        {name: "common/gettext.js", format: "iife"},
        {name: "web/js/colors.js", format: "iife"},
        {name: "web/js/glyph.js", format: "iife"},
        {name: "web/js/util.js", format: "iife"},
        {name: "web/js/override.js", format: "native"},
      ];
      
      const projectRoot = path.resolve(process.cwd());
      const outputFile = path.join(projectRoot, this.options.outputDir, this.options.outputFileName);
      
      this.log(`Generating external libraries file: ${outputFile}`);
      
      let combinedLibraries = "// Combined external libraries for NOC\n";
      combinedLibraries += "// Generated: " + new Date().toISOString() + "\n\n";
      // combinedLibraries += "(function() {\n";
      
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
      
      // combinedLibraries += "\n})();";
      
      if(!fs.existsSync(path.dirname(outputFile))){
        fs.mkdirSync(path.dirname(outputFile), {recursive: true});
      }
      
      fs.writeFileSync(outputFile, combinedLibraries);
      
      this.log(`External libraries file generated successfully: ${outputFile}`);
    } catch(error){
      this.logError(error as Error, "Failed to generate external libraries file");
    }
  }
  
  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[ExternalLibsPlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[ExternalLibsPlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }
}