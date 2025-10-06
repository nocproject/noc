import {build} from "esbuild";
import * as fs from "fs";
import {workers} from "./scripts/bundles/monaco-workers.ts";

const buildOption = {
  bundle: true,
  minify: true,
  sourcemap: false,
  format: "iife" as const,
  target: ["es2020"],
  // platform: "browser" as const,
  tsconfig: "tsconfig.json",
};

const generatedFile = "scripts/bundles/monaco.generated.ts";

if(fs.existsSync(generatedFile)){
  fs.unlinkSync(generatedFile);
}

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
    let monacoSource = fs.readFileSync("scripts/bundles/monaco.ts", "utf-8");

    for(const [label, code] of Object.entries(workerCodes)){
      const placeholder = `/*${label}_WORKER_CODE*/ ""`;
      monacoSource = monacoSource.replace(
        placeholder,
        JSON.stringify(code),
      );
    }

    fs.writeFileSync(generatedFile, monacoSource);

    await build({
      ...buildOption,
      loader: {
        ".ttf": "dataurl",
      },
      entryPoints: [generatedFile],
      outfile: "pkg/monaco/monaco.js",
    });

    console.log("Monaco bundle built successfully!");
    return;
  }
  if(bundleName === "micromark"){
    const entryPoints = `scripts/bundles/${bundleName}.ts`;
    const outfile = `pkg/${bundleName}/${bundleName}.js`;
    // const globalName = bundleName;

    await build({
      entryPoints: [entryPoints],
      outfile,
      ...buildOption,
    });

    console.log(`${bundleName} bundle built successfully!`);
    return;
  }

  console.error(
    `Usage: node build-bundle.ts <micromark|monaco>\nAvailable bundles: micromark, monaco`,
  );
  process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
}); 