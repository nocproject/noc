import * as crypto from "crypto";
import type {BuildOptions, OnLoadArgs, PluginBuild} from "esbuild";
import {build} from "esbuild";
import * as fs from "fs";
import * as path from "path";
import {workers} from "./scripts/bundles/monaco-workers.ts";

const outputDir = "dist";

const buildOption = {
  bundle: true,
  minify: true,
  sourcemap: false,
  sourcesContent: false,
  format: "iife" as const,
  target: ["es2020"],
  tsconfig: "tsconfig.json",
  loader: {
    ".png": "dataurl" as const,
  },
};

// List of bundles to build: [entryPoint, name]
const bundles: {entry: string; name: string}[] = [
  {entry: "scripts/bundles/micromark.ts", name: "micromark"},
  {entry: "scripts/bundles/leaflet.ts", name: "leaflet"},
  {entry: "scripts/bundles/joint/index.ts", name: "joint"},
  // monaco is special — added below
];

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

async function buildMonacoWorkers(): Promise<Record<string, string>>{
  const workerCodes: Record<string, string> = {};
  for(const worker of workers){
    try{
      const result = await build({
        entryPoints: [worker.entry],
        write: false,
        ...buildOption,
      });
      const code = (result as {outputFiles: {text: string}[]})
        .outputFiles[0].text;
      workerCodes[worker.label] = Buffer.from(code).toString("base64");
      console.log(`Worker ${worker.name} built`);
    } catch(error){
      console.error(`Failed to build worker ${worker.name}:`, error);
      throw error;
    }
  }
  return workerCodes;
}

async function buildBundle(entry: string, name: string, extraOptions: Partial<BuildOptions> = {}): Promise<{js: string; css: string}>{
  const result = await build({
    ...buildOption,
    ...extraOptions,
    entryPoints: [entry],
    write: false,
    outdir: "out", // required for write:false with multiple outputs
  });

  let js = "";
  let css = "";

  for(const file of(result as {outputFiles: {path: string; text: string}[]}).outputFiles){
    if(file.path.endsWith(".css")){
      css += file.text;
    } else if(file.path.endsWith(".js")){
      js += file.text;
    }
  }

  console.log(`Bundle "${name}" built (js: ${js.length} bytes, css: ${css.length} bytes)`);
  return {js, css};
}

function contentHash(content: string): string{
  return crypto.createHash("md5").update(content).digest("hex").slice(0, 8);
}

function cleanOldFiles(pattern: RegExp): void{
  const files = fs.readdirSync(outputDir);
  for(const file of files){
    if(pattern.test(file)){
      fs.unlinkSync(path.join(outputDir, file));
    }
  }
}

function updateHtmlFiles(jsFileName: string, cssFileName: string): void{
  const htmlFiles = fs.readdirSync(outputDir).filter(f => f.startsWith("index") && f.endsWith(".html"));
  for(const htmlFile of htmlFiles){
    const filePath = path.join(outputDir, htmlFile);
    let content = fs.readFileSync(filePath, "utf8");
    content = content.replace(/libs-bundle[^"]*\.js/, jsFileName);
    content = content.replace(/libs-bundle[^"]*\.css/, cssFileName);
    fs.writeFileSync(filePath, content);
    console.log(`Updated ${filePath}`);
  }
}

async function main(){
  const allJs: string[] = [];
  const allCss: string[] = [];

  // Build regular bundles
  for(const bundle of bundles){
    const {js, css} = await buildBundle(bundle.entry, bundle.name);
    allJs.push(`/* ${bundle.name} */\n${js}`);
    if(css) allCss.push(`/* ${bundle.name} */\n${css}`);
  }

  // Build monaco (special case with workers + css loader)
  const workerCodes = await buildMonacoWorkers();
  const {js: monacoJs, css: monacoCss} = await buildBundle(
    "scripts/bundles/monaco.ts",
    "monaco",
    {
      loader: {".ttf": "dataurl"},
      plugins: [monacoWorkerPlugin(workerCodes)],
    },
  );
  allJs.push(`/* monaco */\n${monacoJs}`);
  if(monacoCss) allCss.push(`/* monaco */\n${monacoCss}`);

  // Combine content
  const jsContent = allJs.join("\n");
  const cssContent = allCss.join("\n");

  // Generate hashed filenames
  const jsHash = contentHash(jsContent);
  const cssHash = contentHash(cssContent);
  const jsFileName = `libs-bundle-${jsHash}.js`;
  const cssFileName = `libs-bundle-${cssHash}.css`;

  // Clean old libs-bundle files
  cleanOldFiles(/^libs-bundle.*\.(js|css)(\.map)?$/);

  // Write files
  fs.writeFileSync(path.join(outputDir, jsFileName), jsContent);
  console.log(`\nJS written to ${outputDir}/${jsFileName} (${jsContent.length} bytes)`);

  fs.writeFileSync(path.join(outputDir, cssFileName), cssContent);
  console.log(`CSS written to ${outputDir}/${cssFileName} (${cssContent.length} bytes)`);

  // Update HTML files
  updateHtmlFiles(jsFileName, cssFileName);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
