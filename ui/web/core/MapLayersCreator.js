//---------------------------------------------------------------------
// NOC.core.MapLayersCreator
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MapLayersCreator");

Ext.define("NOC.core.MapLayersCreator", {
  validLayerValues: [
    "osm",
    "google_roadmap",
    "google_hybrid",
    "google_sat",
    "google_terrain",
    "yandex_roadmap",
    "yandex_hybrid",
    "yandex_sat",
  ],
  defaultOptions: {
    translator: function(s){
      return s;
    },
    layersControl: {},
    default_layer: "",
    yandex_supported: false,
    allowed_layers: {enable_osm: true},
  },
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
  run: function(scope){
    var translator = this.getTranslator(),
      optionsLayersControl = this.getLayersControl(),
      optionsDefaultLayer = this.getDefaultLayer(),
      yandex_supported = this.isYandexSupported(),
      optionsAllowedLayers = this.getAllowedLayers(),
      default_layer_name = "osm";

    if(!this.validate_def_layer(optionsDefaultLayer)){
      console.warn("Default layer name is not valid", optionsDefaultLayer, "Using osm");
    } else{
      default_layer_name = optionsDefaultLayer;
    }

    if(!this.validate_allowed_layers(optionsAllowedLayers)){
      console.warn("Allowed layers is not valid", optionsAllowedLayers);
    }

    var baseLayers = {
      osm: optionsAllowedLayers.enable_osm
        ? [
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {}),
          translator("OpenStreetMap"),
        ]
        : undefined,
      google_roadmap: optionsAllowedLayers.enable_google_roadmap
        ? [
          L.tileLayer("https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
            subdomains: ["mt0", "mt1", "mt2", "mt3"],
          }),
          translator("Google Roadmap"),
        ]
        : undefined,
      google_hybrid: optionsAllowedLayers.enable_google_hybrid
        ? [
          L.tileLayer("https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}", {
            subdomains: ["mt0", "mt1", "mt2", "mt3"],
          }),
          translator("Google Hybrid"),
        ]
        : undefined,
      google_sat: optionsAllowedLayers.enable_google_sat
        ? [
          L.tileLayer("https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", {
            subdomains: ["mt0", "mt1", "mt2", "mt3"],
          }),
          translator("Google Satellite"),
        ]
        : undefined,
      google_terrain: optionsAllowedLayers.enable_google_terrain
        ? [
          L.tileLayer("https://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}", {
            subdomains: ["mt0", "mt1", "mt2", "mt3"],
          }),
          translator("Google Terrain"),
        ]
        : undefined,
      yandex_roadmap:
        optionsAllowedLayers.enable_yandex_roadmap && yandex_supported
          ? [L.yandex("yandex#map"), translator("Yandex Roadmap")]
          : undefined,
      yandex_hybrid:
        optionsAllowedLayers.enable_yandex_hybrid && yandex_supported
          ? [L.yandex("yandex#hybrid"), translator("Yandex Hybrid")]
          : undefined,
      yandex_sat:
        optionsAllowedLayers.enable_yandex_sat && yandex_supported
          ? [L.yandex("yandex#satellite"), translator("Yandex Satellite")]
          : undefined,
    };

    var default_layer = baseLayers[default_layer_name];
    if(default_layer){
      default_layer = default_layer[0];
    } else{
      console.warn("Layer not found", default_layer_name, "Using osm");
      default_layer = baseLayers.osm[0];
    }

    scope.map.addLayer(default_layer);

    // Generate object
    // {
    //     "<someName1>": layer1,
    //     "<someName2>": layer2
    // }
    var baseLayersToAdd = {};
    Object.keys(baseLayers).forEach(function(key){
      if(baseLayers[key]){
        baseLayersToAdd[baseLayers[key][1]] = baseLayers[key][0];
      }
    });

    scope.layersControl = L.control.layers(baseLayersToAdd, {}, optionsLayersControl);

    scope.layersControl.addTo(scope.map);
  },
});
