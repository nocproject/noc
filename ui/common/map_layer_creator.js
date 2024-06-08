//L       - Leaflet
//me      - object
//options - layersControl 
//          translator
//          default_layer = [
//              osm, 
//              google_roadmap, google_hybrid, google_sat, google_terrain, 
//              yandex_roadmap, yandex_hybrid, yandex_sat
//          ]
//          allowed_layers = {
//              enable_osm : true,
//              enable_google_roadmap : false,
//              ...
//          }
//          yandex_supported
class MapLayersCreator{
    constructor () {

    }
    validate_def_layer = function(s) {
        var valid_values = [
            "osm", 
            "google_roadmap", "google_hybrid", "google_sat", "google_terrain", 
            "yandex_roadmap", "yandex_hybrid", "yandex_sat"
        ]

        return valid_values.includes(s)
    }
    validate_allowed_layers = function(layers) {
        Object.keys(layers).forEach(e => {
            if (!this.validate_def_layer(e.replace("enable_", ""))) {
                return false
            }
        });
        return true
    }
    run = function(L, me, options={}) {
        var ___ = options.translator ? options.translator : function(s) { return s}
        var optionsLayersControl = options.layersControl ? options.layersControl : {}
        var optionsDefaultLayer  = options.default_layer ? options.default_layer : ""
        var yandex_supported     = options.yandex_supported ? options.yandex_supported : false
        var optionsAllowedLayers = options.allowed_layers ? options.allowed_layers : {"enable_osm": true}

        var default_layer_name = "osm"
        if (!this.validate_def_layer(optionsDefaultLayer)) {
            console.warn("Default layer name is not valid", optionsDefaultLayer, "Using osm")
        } else {
            default_layer_name = optionsDefaultLayer
        }

        if (!this.validate_allowed_layers(optionsAllowedLayers)) {
            console.warn("Allowed layers is not valid", optionsAllowedLayers)
        }

        var baseLayers = {
            osm : (optionsAllowedLayers.enable_osm ? [ 
                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", 
                    {
                        
                    }
                ), ___("OpenStreetMap")
            ] : undefined),

            google_roadmap : (optionsAllowedLayers.enable_google_roadmap ? [ 
                L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                    {
                        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
                    }
                ), ___("Google Roadmap") 
            ] : undefined),
            google_hybrid : (optionsAllowedLayers.enable_google_hybrid ? [ 
                L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',
                    {
                        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
                    }
                ), ___("Google Hybrid") 
            ] : undefined),
            google_sat : (optionsAllowedLayers.enable_google_sat ? [ 
                L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    {
                        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
                    }
                ), ___("Google Satellite") 
            ] : undefined),
            google_terrain : (optionsAllowedLayers.enable_google_terrain ? [ 
                L.tileLayer('https://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
                    {
                        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
                    }
                ), ___("Google Terrain") 
            ] : undefined),

            yandex_roadmap : (optionsAllowedLayers.enable_yandex_roadmap && yandex_supported ? [  
                L.yandex('yandex#map'), ___("Yandex Roadmap") 
            ] : undefined),
            yandex_hybrid : (optionsAllowedLayers.enable_yandex_hybrid && yandex_supported ? [ 
                L.yandex('yandex#hybrid'), ___("Yandex Hybrid") 
            ] : undefined),
            yandex_sat : (optionsAllowedLayers.enable_yandex_sat && yandex_supported ? [  
                L.yandex('yandex#satellite'), ___("Yandex Satellite") 
            ] : undefined),
        }

        var default_layer = baseLayers[default_layer_name]
        if (default_layer) {
            default_layer = default_layer[0]
        } else {
            console.warn("Layer not found", default_layer_name, "Using osm")
            default_layer = baseLayers.osm[0]
        }

        me.map.addLayer(default_layer);

        // Generate object 
        // {
        //     "<someName1>": layer1,
        //     "<someName2>": layer2
        // }
        var baseLayersToAdd = {}
        Object.keys(baseLayers).forEach(function(key, index) {
            if (baseLayers[key]) {
                baseLayersToAdd[baseLayers[key][1]] = baseLayers[key][0];
            }
        });

        me.layersControl = L.control.layers(baseLayersToAdd, {}, optionsLayersControl)
        
        me.layersControl.addTo(me.map);
    }
}

mapLayersCreator = new MapLayersCreator()
