import type {Plugin} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import type {Language} from "../builders/BaseBuilder.ts";

interface LanguagePluginOptions {
  debug: boolean;
  isDev: boolean;
  outputDir: string;
  cacheDir: string;
  languages: Language[];
  language?: Language;
}

export class LanguagePlugin{
  private readonly options: LanguagePluginOptions;
  private readonly translationsDir = "web/translations";
  private readonly localeDir = "web/locale";
  
  constructor(options: LanguagePluginOptions){
    this.options = options;
  }
  
  getPlugin(): Plugin{
    return {
      name: "language-plugin",
      setup: (build) => {
        build.onResolve({filter: /^locale-/}, (args) => ({
          path: args.path,
          namespace: "locale",
        }));
        build.onLoad({filter: /.*/, namespace: "locale"}, (args) => {
          const lang = args.path.split("-")[1];
          return {
            contents: this.generateLocaleContent(lang),
            loader: "js",
          };
        });
      },
    };
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

  private generateLocaleContent(lang: string): string{
    try{
      const projectRoot = path.resolve(process.cwd());
      const translationPath = this.translateFiles(projectRoot, this.translationsDir, lang);
      const gettextTemplatePath = path.join(projectRoot, this.localeDir, "gettext.js");
      const templateContent = fs.readFileSync(gettextTemplatePath, "utf8");
      const extLocalePath = path.join(projectRoot, this.localeDir, `${lang}/ext-locale-${lang}.js`);
      const extLocale = fs.readFileSync(extLocalePath, "utf8") || "" + "\n";

      let translations = {};
      if(fs.existsSync(translationPath)){
        const translationContent = fs.readFileSync(translationPath, "utf8");
        translations = JSON.parse(translationContent);
        translations = Object.entries(translations).reduce((acc: Record<string, any>, [key, value]: [string, any]) => { // eslint-disable-line @typescript-eslint/no-explicit-any
          acc[key] = Array.isArray(value) ? value[1] || "" : value;
          return acc;
        }, {});
      }
      return extLocale + templateContent
        .replace(/{locale}/g, lang)
        .replace(/"{translations}"/g, JSON.stringify(translations));
    } catch(error){
      this.logError(error as Error, `Failed to generate locale content for ${lang}`);
      return "";
    }
  }
}