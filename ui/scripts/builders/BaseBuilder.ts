import type * as astring from "astring";
import type * as esbuild from "esbuild";
import type * as espree from "espree";
import fs from "fs-extra";
import path from "path";
import {NocLoaderPlugin} from "../plugins/NocLoaderPlugin.ts";
import {ReplaceMethodsPlugin} from "../plugins/ReplaceMethodsPlugin.ts";
// import {ApplicationLoaderPlugin} from "../plugins/ApplicationLoaderPlugin.ts";
// import {CopyLibPlugin} from "../plugins/CopyLibPlugin.ts";
import {AliasPlugin} from "../plugins/AliasPlugin.ts";
import {HtmlPlugin} from "../plugins/HtmlPlugin.ts";
import {LoggerPlugin} from "../plugins/LoggerPlugin.ts";
import type {MethodReplacement} from "../visitors/MethodReplaceVisitor.ts";

export interface BuilderOptions {
  buildDir: string;
  entryPoint: string;
  pluginDebug: boolean;
  htmlTemplate?: string;
  libDir?: string;
  cacheDir: string;
  assetsDir: string;
  isDev: boolean;
  toReplaceMethods?: MethodReplacement[];
  esbuildOptions: Partial<esbuild.BuildOptions>;
  parserOptions?: espree.Options;
  generateOptions?: astring.Options;
  cssEntryPoints?: string[];
  cssOutdir?: string;
  aliases?: Record<string, string>;
}

export abstract class BaseBuilder{
  abstract readonly className: string;
  protected readonly options: BuilderOptions;
  protected context?: esbuild.BuildContext;

  constructor(options: BuilderOptions){
    this.options = options;
  }

  // this method shares ProdBuilder and DevBuilder classes 
  protected async clearBuildDir(): Promise<void>{
    const entryBasename = path.basename(this.options.entryPoint, path.extname(this.options.entryPoint));
    const filePattern = new RegExp(`^${entryBasename}*`);
    
    await fs.emptyDir(this.options.cacheDir!);
    console.log(`Cleaned ${this.options.cacheDir} directory`);

    const indexHtmlPath = path.join(this.options.buildDir, "index.html");
    if(await fs.pathExists(indexHtmlPath)){
      await fs.remove(indexHtmlPath);
      console.log(`Removed index.html file`);
    }
    await fs.remove(`${this.options.buildDir}/${this.options.assetsDir}`);
    console.log(`Cleaned ${this.options.assetsDir} directory`);

    for(const file of await fs.readdir(this.options.buildDir)){
      if(filePattern.test(file)){
        const filePath = path.join(this.options.buildDir, file);
        await fs.remove(filePath);
        console.log(`Removed bundle: ${file}`);
      }
    }
    console.log(`Cleared bundle files matching pattern: '${filePattern}' and styles in ${this.options.buildDir} directory`);
  }

  protected async initialize(): Promise<void>{
    await fs.ensureDir(this.options.buildDir);
    await this.clean();
  }

  protected getBaseBuildOptions(): esbuild.BuildOptions{
    const nocPlugin = new NocLoaderPlugin({
      basePath: process.cwd(),
      paths: {"NOC": "web"},
      entryPoint: this.options.entryPoint,
      debug: this.options.pluginDebug,
      parserOptions: this.options.parserOptions,
    });
    
    const removePlugin = new ReplaceMethodsPlugin({
      toReplaceMethods: this.options.toReplaceMethods,
      debug: this.options.pluginDebug,
      parserOptions: this.options.parserOptions,
      generateOptions: this.options.generateOptions,
    });
    // const applicationPlugin = new ApplicationLoaderPlugin({
    //   basePath: process.cwd(),
    //   paths: {"NOC": "src/ui"},
    //   entryPoint: this.options.entryPoint,
    //   debug: this.options.pluginDebug,
    //   parserOptions: this.options.parserOptions,
    // });
    // const cssPlugin = new CssPlugin({
    //   entryPoints: this.options.cssEntryPoints || [],
    //   isDev: this.options.isDev,
    //   debug: this.options.pluginDebug,
    // });
    // const plugins = [
    //   applicationPlugin.getPlugin(),
    //   cssPlugin.getPlugin(),
    // ];
    // if(this.options.libDir){
    //   const copyLibPlugin = new CopyLibPlugin({
    //     sourcePath: this.options.libDir,
    //     targetDir: this.options.buildDir,
    //   });
    //   plugins.push(copyLibPlugin.getPlugin());
    // }
    const plugins = [
      // externalLibsPlugin.getPlugin(),
      nocPlugin.getPlugin(),
    ];
    if(!this.options.isDev){
      plugins.push(removePlugin.getPlugin());
    }
    if(this.options.htmlTemplate){
      const htmlPlugin = new HtmlPlugin({
        buildDir: this.options.buildDir,
        templatePath: path.join(process.cwd(), this.options.htmlTemplate),
        isDev: this.options.isDev,
        mode: "create",
        patternForReplace: {
          "app-": [".js", ".css"],
        },
      });
      plugins.push(htmlPlugin.getPlugin());
    }
    if(this.options.aliases){
      const aliasPlugin = new AliasPlugin({
        aliases: this.options.aliases,
        debug: this.options.pluginDebug,
      });
      plugins.push(aliasPlugin.getPlugin());
    }
    return {
      entryPoints: [
        this.options.entryPoint,
        ...(this.options.cssEntryPoints || []),
      ],
      outdir: this.options.buildDir,
      plugins: this.options.isDev ? [
        ...plugins,
        new LoggerPlugin().getPlugin(),
      ] : plugins,
      ...this.options.esbuildOptions,
      loader: {
        ".png": "file",
        ".gif": "file",
        ".jpg": "file",
        ".jpeg": "file",
        ".svg": "file",
        ".eot": "file",
        ".woff": "file",
        ".woff2": "file",
        ".ttf": "file",
      },
      assetNames: `${this.options.assetsDir}/[name]-[hash]`,
    };
  }

  abstract start(): Promise<void>;
  abstract clean(): Promise<void>;
  abstract stop(): Promise<void>;
}
