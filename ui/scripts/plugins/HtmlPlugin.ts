import type {BuildResult, Plugin} from "esbuild";
import * as esbuild from "esbuild";
import fs from "fs-extra";
import * as path from "path";
import type {Language, Theme} from "../builders/BaseBuilder.ts";

type MetafileOutput = {
  bytes: number;
  inputs: {
    [path: string]: {
      bytesInOutput: number;
    };
  };
  imports: {
    path: string;
    kind: esbuild.ImportKind | "file-loader";
    external?: boolean;
  }[];
  exports: string[];
  entryPoint?: string;
  cssBundle?: string;
};

type HtmlPluginMode = "create" | "update";

interface HtmlPluginOptions {
  buildDir: string;
  templatePath: string;
  isDev: boolean;
  mode: HtmlPluginMode;
  theme: Theme;
  themes: Theme[];
  language: Language;
  languages: Language[];
  patternForReplace: Record<string, string[]>;
}

export class HtmlPlugin{
  private readonly options: HtmlPluginOptions;

  constructor(options: HtmlPluginOptions){
    this.options = options;
  }

  getPlugin(): Plugin{
    return {
      name: "html",
      setup: (build: esbuild.PluginBuild): void => {
        build.onEnd(async(result: BuildResult) => {
          if(!result.metafile) return;

          try{
            if(this.options.isDev){
              console.log("Dev build completed. Updating HTML...");
              await this.HTML_forDev(result.metafile.outputs);
            } else{ 
              await this.createHtmlFiles(result.metafile.outputs);
            }
          } catch(error){
            console.error("Error updating HTML:", error);
          }
        });
      },
    };
  }
  private async createHtmlFiles(
    outputs: Record<string, MetafileOutput>,
  ): Promise<void>{
    const filesname = this.options.templatePath.replace(/.html$/, "-prod.html");
    const patternForReplace = {
      "app-prod": [".css"],
      "app": [".js"],
      "ext-locale": [".js"],
      "theme": [".js", ".css"],
      "external": [".js"],
    };
    const toReplaceFiles = Object.keys(outputs).map(file => file.replace(this.options.buildDir + "/", ""))
      .filter((file) => {
        for(const [pattern, exts] of Object.entries(patternForReplace)){
          if(file.startsWith(pattern) && exts.some(ext => file.endsWith(ext))){
            return true;
          }
        }
        return false; 
      });
    const externalLibs = this.searchFile("external", ".js");
    const htmlCache = await fs.readFile(filesname, "utf8");
    if(externalLibs){
      toReplaceFiles.push(externalLibs);
    } else{
      throw new Error(`External libraries file not found in ${this.options.buildDir}`);
    }
    for(const language of this.options.languages){
      for(const theme of this.options.themes){
        const outputFile = `${this.options.buildDir}/index.${theme}.${language}.html`;
        toReplaceFiles.push(this.searchFile(`theme-${theme}`, ".js") || "");
        const files = toReplaceFiles.filter(file => !file.startsWith("theme-") || file.startsWith(`theme-${theme}-`));
        let html = this.addThemeAttribute(htmlCache, theme);
        html = this.setLanguage(html, language);
        for(const file of files){
          html =this.replaceHtmlAttributes(html, file.split("-")[0] + "-", path.extname(file), files);
        }
        await fs.writeFile(outputFile, html);
      }
    }
  }

  private async HTML_forDev(
    outputs: Record<string, MetafileOutput>,
  ): Promise<void>{
    const toReplaceFiles = Object.keys(outputs).map(file => file.replace(this.options.buildDir + "/", ""))
      .filter((file) => {
        for(const [pattern, exts] of Object.entries(this.options.patternForReplace)){
          if(file.startsWith(pattern) && exts.some(ext => file.endsWith(ext))){
            return true;
          }
        }
        return false; 
      });

    let html = this.options.mode === "create"
      ? await fs.readFile(this.options.templatePath, "utf8")
      : await fs.readFile(`${this.options.buildDir}/index.html`, "utf8");

    html = this.addThemeAttribute(html, this.options.theme);
    html = this.setLanguage(html, this.options.language);
    
    for(const [pattern, exts] of Object.entries(this.options.patternForReplace)){
      for(const ext of exts){
        html = this.replaceHtmlAttributes(html, pattern, ext, toReplaceFiles);
      }
    }

    if(this.options.isDev && this.options.mode === "create"){
      const liveReloadScript =
        '  <script>new EventSource("/esbuild").addEventListener("change", () => location.reload());</script>';
      html = html.replace("</head>", `${liveReloadScript}\n</head>`);
    }

    await fs.writeFile(`${this.options.buildDir}/index.html`, html);
  }

  private replaceHtmlAttributes(html: string, pattern: string, suffix: string, toReplace: string[]): string{
    const regex = /(href|src)=["']([^"']*)["']/gi;
    
    return html.replace(regex, (match, attribute, value) => {
      if(value.startsWith(pattern) && value.endsWith(suffix)){
        let replacement = toReplace.find(file => file.startsWith(pattern) && file.endsWith(suffix));
        if(!this.options.isDev){
          replacement = `/ui/${replacement}`;
        }
        if(replacement !== undefined){
          return `${attribute}="${replacement}"`;
        }
      }

      return match;
    });
  }

  private addThemeAttribute(html: string, theme: Theme): string{
    return html.replace(/data-theme=["'][^"']*["']/i, `data-theme="${theme}"`);
  }

  private setLanguage(html: string, language: Language): string{
    let jsonFile = `/ui/web/translations/${language}.json`;
    if(!this.options.isDev){
      jsonFile = this.searchLanguageFile(language);
    }
    return html.replace(/<html[^>]*lang=["'][^"']*["'][^>]*>/i, (match) => {
      if(match.includes("lang=")){
        return match.replace(/lang=["'][^"']*["']/i, `lang="${language}"`);
      } else{
        return match.replace("<html", `<html lang="${language}"`);
      }
    })
      .replace(/<link[^>]*rel=["']gettext["'][^>]*>/i, `<link rel="gettext" href="${jsonFile}" lang="${language}">`);
  }

  private searchLanguageFile(language: Language): string{
    if(language === "en"){
      return "/ui/web/translations/en.json"; // default
    }
    const matchedFile = this.searchFile(language, ".json");
    if(!matchedFile){
      throw new Error(`Translation file for language "${language}" not found in ${this.options.buildDir}`);
    }
    return `/ui/${matchedFile}`;
  }

  private searchFile(basename: string, suffix: string): string | undefined{
    const files = fs.readdirSync(this.options.buildDir);
    const pattern = new RegExp(`^${basename}-[a-f0-9]{8}\\${suffix}$`);
    return files.find(file => pattern.test(file));
  }
}
