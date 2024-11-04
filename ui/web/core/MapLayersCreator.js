//---------------------------------------------------------------------
// NOC.core.MapLayersCreator
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MapLayersCreator");

Ext.define("NOC.core.MapLayersCreator", {
  defaultOptions: {
  //options - layersControl
  //          translator
  //          default_layer = [
  //              osm,
  //              google_roadmap, google_hybrid, google_sat, google_terrain,
  //              tile1, tile2, tile3,
  //              yandex_roadmap, yandex_hybrid, yandex_sat
  //          ]
  //          allowed_layers = {
  //              enable_osm : true,
  //              enable_google_roadmap : false,
  //              ...
  //          }
  //          yandex_supported
    translator: function(s){
      return s;
    },
    default_layer: "",
    layersControl: {},
    allowed_layers: {
      enable_osm: true,
    },
    yandex_supported: false,
  },
  //
  validLayerValues: [
    "osm",
    "google_roadmap",
    "google_hybrid", "google_sat", "google_terrain",
    "tile1", "tile2", "tile3",
    "yandex_roadmap", "yandex_hybrid", "yandex_sat",
  ],
  //
  constructor: function(options){
    this.options = Ext.apply({}, options, this.defaultOptions);
  },
  //
  getTranslator: function(){
    return this.options.translator;
  },
  //
  getLayersControl: function(){
    return this.options.layersControl;
  },
  //
  getDefaultLayer: function(){
    return this.options.default_layer;
  },
  //
  isYandexSupported: function(){
    return this.options.yandex_supported;
  },
  //
  getAllowedLayers: function(){
    return this.options.allowed_layers;
  },
  //
  validate_def_layer: function(s){
    return this.validLayerValues.includes(s);
  },
  //
  validate_allowed_layers: function(layers){
    Object.keys(layers).forEach((e) => {
      if(!this.validate_def_layer(e.replace("enable_", ""))){
        return false;
      }
    });
    return true;
  },
  //
  createTileLayer: function(url, options = {}){
    return L.tileLayer(url, options);
  },
  //
  createGoogleLayer: function(type){
    const types = {
      roadmap: "m",
      hybrid: "s,h",
      satellite: "s",
      terrain: "p",
    };
    return this.createTileLayer(
      `https://{s}.google.com/vt/lyrs=${types[type]}&x={x}&y={y}&z={z}`,
      {subdomains: ["mt0", "mt1", "mt2", "mt3"]},
    );
  },
  //
  createCustomTileLayer: function(config){
    if(config && !config.url) return undefined;
    const options = config.subdomains && Array.isArray(config.subdomains) && config.subdomains.length ? {subdomains: config.subdomains} : {};
    return [
      this.createTileLayer(config.url, options),
      config.name,
    ];
  },
  //
  createYandexLayer: function(type){
    const types = {
      roadmap: "map",
      hybrid: "hybrid",
      satellite: "satellite",
    };

    return [
      L.yandex(`yandex#${types[type]}`),
      this.getTranslator()(`Yandex ${type.charAt(0).toUpperCase() + type.slice(1)}`),
    ];
  },
  //
  createBaseLayers: function(translator, isYandexSupported, options){
    return {
      blank: options.enable_blank && [
        this.createTileLayer(""),
        translator("Blank") ,
      ] || undefined,

      osm: options.enable_osm && [
        this.createTileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
        translator("OpenStreetMap") ,
      ] || undefined,

      google_roadmap: options.enable_google_roadmap
            && [ this.createGoogleLayer("roadmap"), translator("Google Roadmap") ] || undefined,

      google_hybrid: options.enable_google_hybrid
            && [ this.createGoogleLayer("hybrid"), translator("Google Hybrid") ] || undefined,

      google_sat: options.enable_google_sat
            && [ this.createGoogleLayer("satellite"), translator("Google Satellite") ] || undefined,

      google_terrain: options.enable_google_terrain
            && [ this.createGoogleLayer("terrain"), translator("Google Terrain") ] || undefined,

      tile1: options.enable_tile1 &&
              this.createCustomTileLayer(NOC.settings.gis.custom.tile1) || undefined,

      tile2: options.enable_tile2 &&
              this.createCustomTileLayer(NOC.settings.gis.custom.tile2) || undefined,

      tile3: options.enable_tile3 &&
              this.createCustomTileLayer(NOC.settings.gis.custom.tile3) || undefined,

      yandex_roadmap: options.enable_yandex_roadmap
            && isYandexSupported && this.createYandexLayer("roadmap") || undefined,
      yandex_hybrid: options.enable_yandex_hybrid
            && isYandexSupported && this.createYandexLayer("hybrid") || undefined,
      yandex_sat: options.enable_yandex_sat
            && isYandexSupported && this.createYandexLayer("satellite") || undefined,
    };
  },
  //
  createLayersControl: function(baseLayers){
    const layersMap = {};
    Object.values(baseLayers).forEach(layer => {
      if(layer){
        layersMap[layer[1]] = layer[0];
      }
    });
    return layersMap;
  },
  //
  getDefaultLayerInstance: function(baseLayers, defaultLayerName){
    const layer = baseLayers[defaultLayerName];
    if(layer){
      return layer[0];
    }
    console.warn("Layer not found", defaultLayerName, "Using osm");
    return baseLayers.osm[0];
  },
  //
  run: function(scope){
    var translator = this.getTranslator(),
      layersControl = this.getLayersControl(),
      defaultLayer = this.getDefaultLayer(),
      yandex_supported = this.isYandexSupported(),
      allowedLayers = this.getAllowedLayers();
    
    if(!this.validate_allowed_layers(allowedLayers)){
      console.warn("Allowed layers is not valid", allowedLayers);
    }

    var baseLayers = this.createBaseLayers(translator, yandex_supported, allowedLayers),
      defaultLayerInstance = this.getDefaultLayerInstance(baseLayers, defaultLayer),
      baseLayersToAdd = this.createLayersControl(baseLayers);
        
    scope.map.addLayer(defaultLayerInstance);
    scope.layersControl = L.control.layers(baseLayersToAdd, {}, layersControl);
    scope.layersControl.addTo(scope.map);
  },
});
