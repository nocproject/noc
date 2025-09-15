import * as esbuild from "esbuild";
import {LanguagePlugin} from "../plugins/LanguagePlugin.ts";
import {BaseBuilder} from "./BaseBuilder.ts";

export class ProdBuilder extends BaseBuilder{
  readonly className: string = "ProdBuilder";

  async start(): Promise<void>{
    try{
      await this.initialize();
      await this.build();
      console.log("Production build completed successfully");
    } catch(error){
      console.error("Production build failed:", error);
      process.exit(1);
    }
  }

  async clean(): Promise<void>{
    await this.clearBuildDir();
  }

  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
    console.log("Prod builder stopped");
  }

  private async build(): Promise<void>{
    const buildOptions = this.getBaseBuildOptions();
    await esbuild.build({
      ...buildOptions,
      entryPoints: [
        ...(Array.isArray(buildOptions.entryPoints) ? buildOptions.entryPoints : []),
        "web/locale/en/ext-locale-en.js",
        "web/locale/ru/ext-locale-ru.js",
        "web/locale/pt_BR/ext-locale-pt_BR.js",
      ],

      plugins: [
        ...(buildOptions.plugins || []),
        new LanguagePlugin({
          debug: this.options.pluginDebug,
          isDev: false,
          outputDir: this.options.buildDir,
        }).getPlugin(),
      ],
    });
  }
}
