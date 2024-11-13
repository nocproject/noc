import type * as astring from "astring";
import type * as esbuild from "esbuild";
import type * as espree from "espree";
import fs from "fs-extra";
import path from "path";
// import {NocLoaderPlugin} from "../plugins/NocLoaderPlugin.ts";
// import {ReplaceMethodsPlugin} from "../plugins/ReplaceMethodsPlugin.ts";
import {ApplicationLoaderPlugin} from "../plugins/ApplicationLoaderPlugin.ts";
import {CopyLibPlugin} from "../plugins/CopyLibPlugin.ts";
import {CssPlugin} from "../plugins/CssPlugin.ts";
import {HtmlPlugin} from "../plugins/HtmlPlugin.ts";
import {LoggerPlugin} from "../plugins/LoggerPlugin.ts";
import type {MethodReplacement} from "../visitors/MethodReplaceVisitor.ts";

export interface BuilderOptions {
  buildDir: string;
  entryPoint: string;
  pluginDebug: boolean;
  cacheDir?: string;
  isDev: boolean;
  toReplaceMethods?: MethodReplacement[];
  esbuildOptions?: Partial<esbuild.BuildOptions>;
  parserOptions?: espree.Options;
  generateOptions?: astring.Options;
  cssEntryPoints?: string[]; 
  cssOutdir?: string;
}

export abstract class BaseBuilder{
  protected readonly options: BuilderOptions;
  protected context?: esbuild.BuildContext;

  constructor(options: BuilderOptions){
    this.options = options;
  }

  // protected async clearBuildDir(): Promise<void>{
  //   await fs.emptyDir(this.options.buildDir);
  //   console.log(`Cleaned ${this.options.buildDir} directory`);
  // }

  protected async clearBuildDir(): Promise<void>{
    const entryBasename = path.basename(this.options.entryPoint, path.extname(this.options.entryPoint));
    const entryExt = path.extname(this.options.entryPoint);
    const pattern = this.options.esbuildOptions?.entryNames || "[name]-[hash]";
    const searchPattern = pattern
      .replace("[name]", entryBasename)
      .replace("bundle", "\\w+\\" + entryExt)
      .replace("[hash]", "\\w+\\" + entryExt);
    const searchSourcemapPattern = searchPattern + ".map";
    const filePattern = new RegExp(`^${searchPattern}$`);
    const sourcemapPattern = new RegExp(`^${searchSourcemapPattern}$`);
    const files = await fs.readdir(this.options.buildDir);

    await fs.emptyDir(this.options.cacheDir!);
    console.log(`Cleaned ${this.options.cacheDir} directory`);

    for(const file of files){
      if(filePattern.test(file)
        || sourcemapPattern.test(file)
        || file.endsWith(".css")
        || file.endsWith(".css.map")
      ){
        const filePath = path.join(this.options.buildDir, file);
        await fs.remove(filePath);
        console.log(`Removed bundle: ${file}`);
      }
    }
    console.log(`Cleared bundle files matching pattern: '${searchPattern}' and styles in ${this.options.buildDir} directory`);
  }

  protected async initialize(): Promise<void>{
    await fs.ensureDir(this.options.buildDir);
    await this.clearBuildDir();
  }

  protected getBaseBuildOptions(): esbuild.BuildOptions{
    // const nocPlugin = new NocLoaderPlugin({
    // basePath: process.cwd(),
    // paths: {"NOC": "web"},
    // entryPoint: this.options.entryPoint,
    // debug: this.options.pluginDebug,
    // parserOptions: this.options.parserOptions,
    // });
    //
    // const removePlugin = new ReplaceMethodsPlugin({
    // toReplaceMethods: this.options.toReplaceMethods,
    // debug: this.options.pluginDebug,
    // parserOptions: this.options.parserOptions,
    // generateOptions: this.options.generateOptions,
    // });
    const applicationPlugin = new ApplicationLoaderPlugin({
      basePath: process.cwd(),
      paths: {"NOC": "src/ui"},
      entryPoint: this.options.entryPoint,
      debug: this.options.pluginDebug,
      parserOptions: this.options.parserOptions,
    });
    const htmlPlugin = new HtmlPlugin(
      this.options.buildDir,
      path.join(process.cwd(), "src/index.html"),
      this.options.isDev,
    );
    const copyLibPlugin = new CopyLibPlugin("lib", this.options.buildDir);
    const cssPlugin = new CssPlugin({
      entryPoints: this.options.cssEntryPoints || [],
      isDev: this.options.isDev,
      debug: this.options.pluginDebug,
    });
    const plugins = [
      htmlPlugin.getPlugin(),
      copyLibPlugin.getPlugin(),
      applicationPlugin.getPlugin(),
      cssPlugin.getPlugin(),
    ];
    // const plugins = this.options.isDev ? [
    //   nocPlugin.getPlugin(),
    // ] : [
    //   nocPlugin.getPlugin(),
    //   removePlugin.getPlugin(),
    // ];
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
    };
  }

  abstract start(): Promise<void>;

  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
  }
}
