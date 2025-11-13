declare global {
    interface Window {
      leafletAPI: typeof LeafletAPI;
      NOC?: {
        settings?: {
          gis?: {
            yandex_supported?: boolean;
          };
        };
      };
      // ymaps?: any;
    }
}

let isPreloaded = false;
let yapiLoaded = false;

function checkYandexSupported(): boolean{
  try{
    return !!(window?.NOC?.settings?.gis?.yandex_supported);
  } catch{
    return false;
  }
}

async function loadYandexModules(): Promise<void>{
  console.log("Initializing Yandex API...");
  if(!yapiLoaded){
    const {default: initYapi} = await import("ymaps" as string);
    await initYapi.load();
    yapiLoaded = true;
  }
  await import("./src/Yandex.js" as string);
  console.log("Yandex API initialized.");
}

const LeafletAPI = {
  preload: async function(): Promise<void>{
    if(isPreloaded){
      console.warn("Leaflet library already preloaded.");
      return;
    }
    
    console.log("Leaflet library preloading started.");
    void import("leaflet");
    console.log(checkYandexSupported());
    if(checkYandexSupported()){
      try{
        await loadYandexModules();
        console.log("Yandex modules loaded successfully.");
      } catch(error){
        console.error("Failed to load Yandex modules:", error);
      }
    }
    
    isPreloaded = true;
    return;
  },
};

window.leafletAPI = LeafletAPI

export default LeafletAPI;