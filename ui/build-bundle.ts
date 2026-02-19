import type {OnLoadArgs, PluginBuild} from "esbuild";
import {build} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import {workers} from "./scripts/bundles/monaco-workers.ts";

const isDev = process.argv.includes("--dev");

const buildOption = {
  bundle: true,
  minify: !isDev,
  sourcemap: isDev,
  sourcesContent: true,
  format: "iife" as const,
  target: ["es2020"],
  // platform: "browser" as const,
  tsconfig: "tsconfig.json",
  loader: {
    ".png": "dataurl" as const,
  },
};

const outputDir = "dist";
// removed generatedFile logic

if(!fs.existsSync(outputDir)){
  fs.mkdirSync(outputDir, {recursive: true});
}

const monacoWorkerPlugin = (workerCodes: Record<string, string>) => ({
  name: "monaco-worker",
  setup(build: PluginBuild){
    build.onLoad({filter: /monaco\.ts$/}, async(args: OnLoadArgs) => {
      let source = await fs.promises.readFile(args.path, "utf8");
      for(const [label, code] of Object.entries(workerCodes)){
        const placeholder = `/*${label}_WORKER_CODE*/ ""`;
        source = source.replace(placeholder, JSON.stringify(code));
      }
      return {
        contents: source,
        loader: "ts",
        resolveDir: path.dirname(args.path),
      };
    });
  },
});

async function buildMonacoWorkers(){
  const workerCodes: Record<string, string> = {};
  for(const worker of workers){
    try{
      const result = await build({
        entryPoints: [worker.entry],
        write: false,
        ...buildOption,
      });
      const code = (result as { outputFiles: { text: string }[] })
        .outputFiles[0].text;
      workerCodes[worker.label] = Buffer.from(code).toString("base64");
      console.log(`Worker ${worker.name} built and captured in memory!`);
    } catch(error){
      console.error(`Failed to build worker ${worker.name}:`, error);
      throw error;
    }
  }
  return workerCodes;
}

async function main(){
  const bundleName = process.argv[2];
  
  if(bundleName === "monaco"){
    const workerCodes = await buildMonacoWorkers();

    await build({
      ...buildOption,
      loader: {
        ".ttf": "dataurl",
      },
      entryPoints: ["scripts/bundles/monaco.ts"],
      plugins: [monacoWorkerPlugin(workerCodes)],
      outfile: `${outputDir}/monaco.js`,
    });

    console.log("Monaco bundle built successfully!");
    return;
  } else{
    let entryPoints = `scripts/bundles/${bundleName}.ts`;
    if(!fs.existsSync(entryPoints)){
      entryPoints = `scripts/bundles/${bundleName}/index.ts`;
    }
    const outfile = `${outputDir}/${bundleName}.js`;

    await build({
      entryPoints: [entryPoints],
      outfile,
      ...buildOption,
    });

    console.log(`${bundleName} bundle built successfully!`);
    return;
  }

}

main().catch((e) => {
  console.error(e);
  process.exit(1);
}); 