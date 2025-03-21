import type {BuildResult, Plugin} from "esbuild";
import * as esbuild from "esbuild";
import fs from "fs-extra";

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
export class HtmlPlugin{
  private readonly buildDir: string;
  private readonly templatePath: string;
  private readonly isDev: boolean;

  constructor(buildDir: string, templatePath: string, isDev: boolean){
    this.buildDir = buildDir;
    this.templatePath = templatePath;
    this.isDev = isDev;
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
    const jsFile = Object.keys(outputs).find((file) => file.endsWith(".js"));
    const cssFile = Object.keys(outputs).find((file) => file.endsWith(".css"));
    if(!jsFile){
      throw new Error("JS file not found in build output");
    }

    if(!cssFile){
      throw new Error("CSS file not found in build output");
    }

    const jsFileName = jsFile.split("/").pop()!;
    const cssFileName = cssFile.split("/").pop()!;
    let html = await fs.readFile(this.templatePath, "utf8");

    html = html.replace(/%JS_BUNDLE%/g, jsFileName);
    html = html.replace(/%CSS_BUNDLE%/g, cssFileName);

    if(this.isDev){
      const liveReloadScript =
        '<script>new EventSource("/esbuild").addEventListener("change", () => location.reload());</script>';
      html = html.replace("</head>", `${liveReloadScript}\n</head>`);
    }

    await fs.writeFile(`${this.buildDir}/index.html`, html);
  }
}
