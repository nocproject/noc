export interface MonacoWorkerConfig {
     name: string;
     entry: string;
     label: string;
   }

export const workers: MonacoWorkerConfig[] = [
  {name: "ts.worker", entry: "node_modules/monaco-editor/esm/vs/language/typescript/ts.worker.js", label: "typescript"},
  {name: "editor.worker", entry: "node_modules/monaco-editor/esm/vs/editor/editor.worker.js", label: "editorWorkerService"},
  {name: "json.worker", entry: "node_modules/monaco-editor/esm/vs/language/json/json.worker.js", label: "json"},
  {name: "css.worker", entry: "node_modules/monaco-editor/esm/vs/language/css/css.worker.js", label: "css"},
  {name: "html.worker", entry: "node_modules/monaco-editor/esm/vs/language/html/html.worker.js", label: "html"},
];