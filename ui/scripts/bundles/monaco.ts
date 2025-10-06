import * as monaco from "monaco-editor";

interface MonacoOptions {
  theme?: string;
  language?: string;
  value?: string;
  readOnly?: boolean;
  minimap?: boolean;
  fontSize?: number;
  fontFamily?: string;
  scrollBeyondLastLine?: boolean;
  lineNumbers?: "on" | "off" | "relative";
  wordWrap?: "off" | "on" | "wordWrapColumn" | "bounded";
  automaticLayout?: boolean;
}

declare global {
  interface Window {
    monaco: typeof monaco;
    monacoAPI: typeof MonacoAPI;
    MonacoEnvironment: typeof MonacoEnvironment;
  }
}

const base64ToString = (base64: string): string => {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  
  for(let i = 0; i < binaryString.length; i++){
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  return new TextDecoder().decode(bytes);
};

const workerMap: Record<string, Worker> = {};

const MonacoEnvironment = {
  getWorker: function(moduleId: string, label: string): Worker{
    label = label === "javascript" ? "typescript" : label;
    
    if(workerMap[label]){
      return workerMap[label];
    }
    const workerCode = workerCodeMap[label] || workerCodeMap["editorWorkerService"];
    if(!workerCode){
      throw new Error(`No worker code found for label: ${label}`);
    }
    const decodedCode = base64ToString(workerCode);
    const workerBlob = new Blob([decodedCode], {type: "application/javascript"});
    const workerUrl = URL.createObjectURL(workerBlob);
    if(!workerUrl || workerUrl === ""){
      throw new Error(`Failed to create worker URL for label: ${label}`);
    } 
    const worker = new Worker(workerUrl);
    workerMap[label] = worker;
    return worker;
  },
  getWorkers: function(): Record<string, Worker>{
    return workerMap;
  },
};

const workerCodeMap: Record<string, string> = {
  editorWorkerService: /*editorWorkerService_WORKER_CODE*/ "",
  json: /*json_WORKER_CODE*/ "",
  css: /*css_WORKER_CODE*/ "",
  html: /*html_WORKER_CODE*/ "",
  typescript: /*typescript_WORKER_CODE*/ "",
};

// create workers at startup
// Object.entries(workerCodeMap).forEach(([label, base64Code]) => {
//   try{
//     const code = base64ToString(base64Code);
    
//     const workerUrl = URL.createObjectURL(
//       new Blob([code], {type: "application/javascript"}),
//     );
    
//     const worker = new Worker(workerUrl);
//     workerMap[label] = worker;
//   } catch(error){
//     console.error("DEBUG error creating worker at startup:", error);
//     throw error;
//   }
// });

const MonacoAPI = {
  create: function(container: HTMLElement, options: MonacoOptions = {}){
    const defaultOptions = {
      theme: "vs-dark",
      language: "javascript",
      value: "",
      readOnly: false,
      minimap: {enabled: true},
      fontSize: 14,
      fontFamily: 'Consolas, "Courier New", monospace',
      lineNumbers: "on" as const,
      wordWrap: "off" as const,
      automaticLayout: true,
    };
    
    const finalOptions = Object.assign({}, defaultOptions, options);
     
    return monaco.editor.create(container, finalOptions);
  },
  
};

window.monaco = monaco;
window.MonacoEnvironment = MonacoEnvironment;
window.monacoAPI = MonacoAPI;

export default MonacoAPI;

