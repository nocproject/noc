//---------------------------------------------------------------------
// NOC.core.ResourceLoader
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
//
// Example use:
// load set of resources
// NOC.core.ResourceLoader.loadSet('leaflet', {
//     yandex: NOC.settings.gis.yandex_supported
// })
// .then(() => {
//     me.createMap(data);
// })
// .catch((error) => {
//     NOC.error(__('Failed to load map resources'));
// });
// load several resources
// NOC.core.ResourceLoader.load([
//     "/ui/pkg/leaflet/leaflet.js",
//     "/ui/pkg/leaflet/leaflet.css",
//     "/ui/pkg/leaflet/yapi.js",
//     "/ui/pkg/leaflet/Yandex.js",
// ])
// .then(() => {
//     me.createMap(data);
// })
// .catch(error => {
//     NOC.error(__('Failed to load map resources'));
// });

console.debug("Defining NOC.core.ResourceLoader");

Ext.define("NOC.core.ResourceLoader", {
  singleton: true,

  loadedResources: {},

  resourceSets: {
    "leaflet": {
      resources: [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet/leaflet.css",
      ],
      optional: {
        "yandex": [
          "/ui/pkg/leaflet/yapi.js",
          "/ui/pkg/leaflet/Yandex.js",
        ],
      },
    },
  },

  loadSet: function(setName, config = {}){
    if(!this.resourceSets[setName]){
      return Promise.reject(`Resource set '${setName}' not found`);
    }

    const set = this.resourceSets[setName];
    let resources = [...set.resources];

    if(set.optional){
      Object.entries(set.optional).forEach(([key, urls]) => {
        if(config[key]){
          resources = resources.concat(urls);
        }
      });
    }

    return this.load(resources);
  },

  load: function(resources){
    if(!Array.isArray(resources)){
      resources = [resources];
    }

    const unloadedResources = resources.filter(url => !this.loadedResources[url]);

    if(!unloadedResources.length){
      return Promise.resolve();
    }

    const jsResources = unloadedResources.filter(url => url.endsWith(".js"));
    const cssResources = unloadedResources.filter(url => url.endsWith(".css"));

    cssResources.forEach(url => {
      this.loadCSS(url);
      this.loadedResources[url] = true;
    });

    return jsResources.reduce((promise, url) => {
      return promise.then(() => {
        return this.loadScript(url).then(() => {
          this.loadedResources[url] = true;
        });
      });
    }, Promise.resolve());
  },

  loadScript: function(url){
    return new Promise((resolve, reject) => {
      Ext.Loader.loadScript({
        url: url,
        onLoad: resolve,
        onError: reject,
      });
    });
  },

  loadCSS: function(url){
    Ext.util.CSS.swapStyleSheet("style-" + Ext.id(), url);
  },
});
