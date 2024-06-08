//----------------------------------------------------------------------
//  Path map
//----------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------
var PathMap = function () {
    this.map = null;
};

PathMap.prototype.run = function(path) {
    var i;
    // Get bounding box
    var x0 = 180.0, y0 = 180.0, x1 = -180.0, y1 = -180.0;
    for(i = 0; i < path.length; i++) {
        var item = path[i];
        x0 = Math.min(x0, item.x);
        x1 = Math.max(x1, item.x);
        y0 = Math.min(y0, item.y);
        y1 = Math.max(y1, item.y);
    }
    // Get center point (@todo: Center of mass?)
    var xc = (x0 + x1) / 2.0,
        yc = (y0 + y1) / 2.0;
    var scale = 12;
    //
    this.map = L.map("map");

    settings = settingsLoader.run()

    mapLayersCreator.run(L, this, {
        default_layer: settings.gis.default_layer, 
        allowed_layers: settings.gis.base,
        yandex_supported: settings.gis.yandex_supported,
        layersControl : {"position": "bottomright"},
    });
    
    var linkFeatures = [];
    for(i = 0; i < path.length - 1; i++) {
        linkFeatures.push({
            type: "Feature",
            geometry: {
                type: "LineString",
                coordinates: [
                    [path[i].x, path[i].y],
                    [path[i + 1].x, path[i + 1].y]
                ]
            }
        });
    }
    L.geoJSON({
        type: "FeatureCollection",
        features: linkFeatures
    }).addTo(this.map);
    // PoPs layer
    var popFeatures = [];
    for(i = 0; i < path.length; i ++) {
        var item = path[i];
        // Build popup
        var popup = ["Managed Objects:"];
        for(var j = 0; j < item.objects.length; j++) {
            popup.push("<a target=_ href='/api/card/view/managedobject/" + item.objects[j].id + "/'>" + item.objects[j].name + "</a>")
        }
        // Place PoP
        popFeatures.push({
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [item.x, item.y]
            },
            properties: {
                popupContent: popup.join("<br>")
            }
        });
    }
    L.geoJSON({
        type: "FeatureCollection",
        features: popFeatures
    }, {
        onEachFeature: function(feature, layer) {
            if(feature.properties && feature.properties.popupContent) {
                layer.bindPopup(feature.properties.popupContent)
            }
        }
    }).addTo(this.map);
    // Set position
    this.map.fitBounds([
        [y0, x0],
        [y1, x1]
    ]);
    // Remove "loading" spinner
    $("#summary").html("");
};
