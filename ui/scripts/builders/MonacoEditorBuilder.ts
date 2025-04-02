import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";
import {HtmlPlugin} from "../plugins/HtmlPlugin.ts";
import {BaseBuilder} from "./BaseBuilder.ts";


interface MonacoWorkerConfig {
  name: string;
  entry: string;
  label?: string; // label for MonacoEnvironment.getWorkerUrl
}

export class MonacoEditorBuilder extends BaseBuilder{
  readonly className = "MonacoEditorBuilder";
  private workersDir: string = "monaco-workers";
  
  private readonly workers: MonacoWorkerConfig[] = [
    {name: "editor.worker", entry: "node_modules/monaco-editor/esm/vs/editor/editor.worker.js", label: "editorWorkerService"},
    {name: "json.worker", entry: "node_modules/monaco-editor/esm/vs/language/json/json.worker", label: "json"},
    {name: "css.worker", entry: "node_modules/monaco-editor/esm/vs/language/css/css.worker", label: "css"},
    {name: "html.worker", entry: "node_modules/monaco-editor/esm/vs/language/html/html.worker", label: "html"},
    {name: "ts.worker", entry: "node_modules/monaco-editor/esm/vs/language/typescript/ts.worker", label: "typescript"},
  ];

  async start(): Promise<void>{
    console.log("Starting Monaco Editor build...");
    
    try{
      this.setBuildOptions();
      await this.initialize();
      await this.generateEntryFile();

      await esbuild.build(this.options.esbuildOptions);
      // await this.copyMonacoCss();
      await this.buildWorkers();
      
      console.log("Monaco Editor build completed successfully!");
      
      // console.log("\nMonaco Editor loader code:");
      // console.log("===============================================");
      // console.log(this.generateLoaderCode());
      // console.log("===============================================");
      
    } catch(error){
      console.error("Error building Monaco Editor:", error);
      throw error;
    }
  }

  async clean(): Promise<void>{
    const files = await fs.readdir(this.options.buildDir);
    const pattern = new RegExp("^monaco-*");
    console.log("Cleaning monaco editor build directory...");
    for(const file of files){
      if(pattern.test(file)){
        fs.removeSync(path.join(this.options.buildDir, file));
        console.log(`${file} removed.`);
      }
    }
  }

  private setBuildOptions(): void{
    this.options.esbuildOptions = {
      ...this.getBaseBuildOptions(),
      entryPoints: [`${this.options.cacheDir}/monaco.js`],
      format: "iife",
      plugins: [
        new HtmlPlugin({
          buildDir: this.options.buildDir,
          templatePath: path.join(process.cwd(), this.options.htmlTemplate!),
          isDev: this.options.isDev,
          mode: "update",
          patternForReplace: {
            "monaco-": [".js", ".css"],
          },
        }).getPlugin(),
      ],
    };
  }

  private generateWorkerMap(): Record<string, string>{
    const map: Record<string, string> = {};
    
    this.workers.forEach(worker => {
      if(worker.label){
        map[worker.label] = `${this.workersDir}/${worker.name}.js`;
      }
      
      if(worker.label === "typescript"){
        map["javascript"] = `${this.workersDir}/${worker.name}.js`;
      }
    });
    
    return map;
  }
  
  private async generateEntryFile(): Promise<void>{
    const entryDir = path.dirname(this.options.buildDir);
    const filename = this.filenameFromEntryPoint(this.options.esbuildOptions.entryPoints!);
    await fs.ensureDir(entryDir);
    
    const workerMap = this.generateWorkerMap();
    const workerMapJson = JSON.stringify(workerMap, null, 2)
      .replace(/"/g, "'")
      .replace(/\n/g, "\n      ");
    
    const entryContent = `
      // Monaco Editor entry file
      import * as monaco from 'monaco-editor';
      
      window.monaco = monaco;
      
      window.MonacoEnvironment = {
        getWorkerUrl: function(workerId, label) {
          const workerMap = ${workerMapJson};
          
          return workerMap[label] || '${this.workersDir}/editor.worker.js';
        }
      };
    `;
    
    await fs.writeFile(filename, entryContent);
    console.log(`Created Monaco Editor entry file at ${filename}`);
  }
  
  private filenameFromEntryPoint(value : string[] | Record<string, string> | { in: string; out: string; }[]): string{
    if(Array.isArray(value)){
      if(value.length > 0 && typeof value[0] === "object" && "in" in value[0]){
        return (value[0] as { in: string; out: string }).in;
      }
      return value[0] as string;
    } else{
      const firstKey = Object.keys(value)[0];
      return firstKey ? value[firstKey] : "monaco.js";
    }
  }
  
  // private async copyMonacoCss(): Promise<void>{
  //   const cssSource = path.resolve(process.cwd(), "node_modules/monaco-editor/min/vs/editor/editor.main.css");
  //   const cssOutName = this.options.isDev ? "monaco-editor.css" : `monaco-editor-${Date.now().toString(36)}.css`;
  //   const cssDest = path.join(this.options.buildDir, cssOutName);
    
  //   await fs.copy(cssSource, cssDest);
  //   console.log(`Copied Monaco Editor CSS to ${cssDest}`);
  // }
  
  private async buildWorkers(): Promise<void>{
    const outputDir = path.join(this.options.buildDir, this.workersDir);
    await fs.ensureDir(outputDir);
    
    for(const worker of this.workers){
      console.log(`Building worker: ${worker.name}...`);

      const result = await esbuild.build({
        entryPoints: [path.resolve(process.cwd(), worker.entry)],
        outdir: outputDir,
        bundle: true,
        format: "iife",
        minify: !this.options.isDev,
        sourcemap: this.options.isDev,
        target: ["es2020"],
      });
      
      if(result.errors.length > 0){
        console.error(`Error building ${worker.name} worker:`, result.errors);
      } else{
        console.log(`Successfully built ${worker.name} worker`);
      }
    }
  }

  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
    console.log("Monaco Editor build stopped");
  }
}