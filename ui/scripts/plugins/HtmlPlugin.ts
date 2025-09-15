import type {BuildResult, Plugin} from "esbuild";
import * as esbuild from "esbuild";
import fs from "fs-extra";
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
  language: Language;
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
            await this.updateHtml(result.metafile.outputs);
          } catch(error){
            console.error("Error updating HTML:", error);
          }
        });
      },
    };
  }

  private async updateHtml(
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
        const replacement = toReplace.find(file => file.startsWith(pattern) && file.endsWith(suffix));
            
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
    return html.replace(/<html[^>]*lang=["'][^"']*["'][^>]*>/i, (match) => {
      if(match.includes("lang=")){
        return match.replace(/lang=["'][^"']*["']/i, `lang="${language}"`);
      } else{
        return match.replace("<html", `<html lang="${language}"`);
      }
    })
      .replace(/<link[^>]*rel=["']gettext["'][^>]*>/i, `<link rel="gettext" href="/ui/web/translations/${language}.json" lang="${language}">`);
  }
}
