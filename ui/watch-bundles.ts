import {spawn} from "child_process";
import * as fs from "fs";
import * as path from "path";

const watchDir = path.resolve(process.cwd(), "scripts/bundles");
const debounceMs = 250;

type RunState = { running: boolean; queued: boolean };

const timers = new Map<string, NodeJS.Timeout>();
const states = new Map<string, RunState>();

function bundleNameFromPath(filePath: string): string | null{
  const rel = path.relative(watchDir, filePath).replace(/\\/g, "/");
  if(!rel || rel.startsWith("..")) return null;
  const parts = rel.split("/");
  if(parts.length === 1){
    const base = parts[0];
    const m = base.match(/^(.*)\.ts$/);
    if(m) return m[1];
    return null;
  }
  // path like "joint/index.ts" or "monaco/something"
  return parts[0];
}

function runBundle(bundle: string){
  const scriptName = `build:${bundle}-dev`;
  const state = states.get(bundle) || {running: false, queued: false};
  if(state.running){
    state.queued = true;
    states.set(bundle, state);
    console.log(`Bundle ${bundle} is running — queued another run`);
    return;
  }

  console.log(`Running ${scriptName}...`);
  state.running = true;
  state.queued = false;
  states.set(bundle, state);

  const child = spawn("pnpm", ["run", scriptName], {stdio: "inherit"});
  child.on("exit", (code) => {
    state.running = false;
    states.set(bundle, state);
    if(state.queued){
      state.queued = false;
      // schedule immediate rerun
      setTimeout(() => runBundle(bundle), 50);
    }
    console.log(`${scriptName} finished with code ${code}`);
  });
}

function scheduleRun(bundle: string){
  if(!bundle) return;
  if(timers.has(bundle)) clearTimeout(timers.get(bundle)!);
  timers.set(bundle, setTimeout(() => {
    timers.delete(bundle);
    runBundle(bundle);
  }, debounceMs));
}

function watch(){
  if(!fs.existsSync(watchDir)){
    console.error(`Watch directory not found: ${watchDir}`);
    process.exit(1);
  }

  console.log(`Watching ${watchDir} for bundle changes...`);

  const watcher = fs.watch(watchDir, {recursive: true}, (eventType, filename) => {
    if(!filename) return;
    const full = path.join(watchDir, filename);
    const bundle = bundleNameFromPath(full);
    if(!bundle) return;
    console.log(`Detected ${eventType} on ${filename} -> bundle: ${bundle}`);
    scheduleRun(bundle);
  });

  process.on("SIGINT", () => {
    watcher.close();
    console.log("Watcher stopped");
    process.exit(0);
  });
}

watch();
