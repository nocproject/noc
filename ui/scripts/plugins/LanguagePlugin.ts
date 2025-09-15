import * as crypto from "crypto";
import type {Plugin} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import type {Language} from "../builders/BaseBuilder.ts";

interface LanguagePluginOptions {
  debug: boolean;
  isDev: boolean;
  outputDir: string;
  language?: Language;
}

export class LanguagePlugin{
  private readonly options: LanguagePluginOptions;
  
  constructor(options: LanguagePluginOptions){
    this.options = options;
  }
  
  getPlugin(): Plugin{
    return {
      name: "theme-plugin",
      setup: (build) => {
        build.onStart(async() => {
          await this.generateLanguageFiles();
        });
      },
    };
  }
  private async generateLanguageFiles(): Promise<void>{
    try{
      const languagesDir = "web/translations";
      const languages = [
        "ru",
        "pt_BR",
      ];
      const projectRoot = path.resolve(process.cwd());
      
      this.log(`Minify translate files for : ${languages.join(",")}`);
      for(const lang of languages){
        try{
          const filePath = this.translateFiles(projectRoot, languagesDir, lang);
          
          if(fs.existsSync(filePath)){
            const json = JSON.parse(fs.readFileSync(filePath, "utf-8"));
            const minified = JSON.stringify(json);
            const hash = crypto.createHash("md5").update(minified).digest("hex").slice(0, 8);
            const outputPath = `${this.options.outputDir}/${lang}-${hash}.json`;
            fs.writeFileSync(outputPath, minified);
            this.log(`${lang}  - ${outputPath}`);
          } else{
            console.warn(`Warning: File not found: ${filePath}`);
          }
        } catch(error){
          this.logError(error as Error, `Error reading library file ${lang}:`);
        }
        this.log(`Minify successfully:`);
      }
    } catch(error){
      this.logError(error as Error, "Failed to generate theme files");
    }
  }
  private log(...args: (string | number | boolean | object)[]): void{
    if(this.options.debug){
      console.log("[LanguagePlugin]", ...args);
    }
  }

  private logError(error: Error, context?: string): void{
    console.error(
      "[LanguagePlugin] Error" + (context ? ` in ${context}` : ""),
    );
    console.error(error);
  }

  private translateFiles(root: string, languagesDir: string, language: string): string{
    return path.join(root,languagesDir, `${language}.json`);
  }
}