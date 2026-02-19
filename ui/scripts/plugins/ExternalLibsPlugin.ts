import * as crypto from "crypto";
import type {Plugin} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import type {Language, Theme} from "../builders/BaseBuilder.ts";

interface ExternalLibsPluginOptions {
  debug: boolean;
  isDev: boolean;
  outputDir: string;
  outputFileName: string;
  theme: Theme;
  language: Language;
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
      },
    };
  }
  
  private async generateExternalLibsFile(): Promise<void>{
    try{
      const projectRoot = path.resolve(process.cwd());
      let outputFile = path.join(projectRoot, this.options.outputDir, this.options.outputFileName);
      let libraryFiles = [
        // Base libs and ExtJS
        {name: "web/js/jsloader.js", format: "iife"},
        {name: `pkg/extjs/ext-all${this.options.isDev ? "-debug" : ""}.js`, format: "native"},
        {name: "pkg/extjs/packages/charts/classic/charts.js", format: "iife"},
        {name: "pkg/jquery/jquery.min.js", format: "iife"},
        
        // CodeMirror and addons
        // {name: "pkg/codemirror/lib/codemirror.js", format: "iife"},
        // {name: "pkg/codemirror/addon/dialog/dialog.js", format: "iife"},
        // {name: "pkg/codemirror/addon/search/search.js", format: "iife"},
        // {name: "pkg/codemirror/addon/search/searchcursor.js", format: "iife"},
        // {name: "pkg/codemirror/addon/selection/active-line.js", format: "iife"},
        // {name: "pkg/codemirror/addon/mode/loadmode.js", format: "iife"},
        // {name: "pkg/codemirror/addon/edit/matchbrackets.js", format: "iife"},
        // {name: "common/diff_match_patch.js", format: "iife"},
        // {name: "pkg/codemirror/addon/merge/merge.js", format: "iife"},
        
        // JointJS
        {name: "pkg/lodash/lodash.min.js", format: "iife"},
        {name: "pkg/backbone/backbone.min.js", format: "iife"},
        {name: "pkg/dagre/dagre.min.js", format: "iife"},
        {name: "pkg/graphlib/graphlib.min.js", format: "iife"},
        {name: "pkg/joint/joint.min.js", format: "iife"},
        {name: "pkg/joint.layout.directedgraph/joint.layout.directedgraph.min.js", format: "iife"},
        {name: "web/wf/workflow/js/joint.element.Tools.js", format: "iife"},
      
        // Other libraries
        // {name: "pkg/moment/moment.min.js", format: "iife"},
        // {name: "pkg/moment-timezone/moment-timezone-with-data-1970-2030.min.js", format: "iife"},
        {name: "pkg/viz-js/viz-standalone.js", format: "iife"},
       
        // Self-made libraries
        // {name: "scripts/bundles/dist/micromark.js", format: "iife"},
        // {name: "scripts/bundles/dist/monaco.js", format: "iife"},
        // {name: "scripts/bundles/dist/leaflet.js", format: "iife"},

        // node_modules
        {name: "node_modules/color-input/dist/color-input.min.js", format: "iife"},
  
        // NOC modules
        {name: "web/js/colors.js", format: "iife"},
        {name: "web/js/glyph.js", format: "iife"},
        {name: "web/js/util.js", format: "iife"},
        {name: "web/js/override.js", format: "native"},
      ];
      
      this.log(`Generating external libraries file: ${outputFile}`);
      
      let combinedLibraries = "// Combined external libraries for NOC\n";
      combinedLibraries += "// Generated: " + new Date().toISOString() + "\n\n";
      // combinedLibraries += "(function() {\n";
      if(this.options.isDev){
        libraryFiles = [
          ...libraryFiles,
          {name: `pkg/extjs/classic/theme-${this.options.theme}/theme-${this.options.theme}.js`, format: "iife"},
        ];
      } 
      for(const libPath of libraryFiles){
        try{
          const filePath = path.join(projectRoot, libPath.name);
          
          if(fs.existsSync(filePath)){
            let content = fs.readFileSync(filePath, "utf-8");
            content = content.replace(/\/\/[#@]\s*sourceMappingURL=.*/g, "");
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
      
      if(!this.options.isDev){
        const hash = crypto.createHash("md5").update(combinedLibraries).digest("hex").slice(0, 8);
        outputFile = outputFile.replace(/(\.js)$/, `-${hash}$1`);
      }

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