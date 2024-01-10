//----------------------------------------------------------------------
//  Alarm heatmap
//----------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------
var Heatmap = function () {
    this.map = null;
};

Heatmap.prototype.initialize = function (lon, lat, zoom) {
    var me = this,
        q = this.parseQuerystring(),
        lon = q.lon ? parseFloat(q.lon) : lon || 37.5077,
        lat = q.lat ? parseFloat(q.lat) : lat || 55.7766,
        scale = q.zoom ? parseInt(q.zoom) : zoom || 11;

    this.heatmap = null;
    this.topology = null;
    this.pops = null;
    this.map = L.map("map");

    // Subscribe to events
    this.map.on("moveend", function() {me.poll_data();});

    // Select view, trigger moveend to poll data
    this.map.setView([lat, lon], scale);

    settings = settingsLoader.run()

    mapLayersCreator.run(L, this, {
        default_layer: settings.gis.default_layer, 
        allowed_layers: settings.gis.base,
        yandex_supported: settings.gis.yandex_supported,
    });
};

Heatmap.prototype.parseQuerystring = function() {
    var q = window.location.search.substring(1),
        vars = q.split("&"),
        r = {}, i, pair;
    for(i = 0; i < vars.length; i++) {
        pair = vars[i].split("=");
        r[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
    }
    return r;
};

Heatmap.prototype.run = function (maintenance, lon, lat, zoom) {
    this.maintenance = maintenance;
    this.initialize(lon, lat, zoom);
};

Heatmap.prototype.poll_data = function () {
    var me = this,
        bbox = me.map.getBounds(),
        w = bbox.getWest(),
        e = bbox.getEast(),
        n = bbox.getNorth(),
        s = bbox.getSouth(),
        zoom = me.map.getZoom(),
        onEachPoP = function(feature, layer) {
            if(feature.properties && feature.properties.alarms > 0 && feature.properties.objects) {
                var text = ["Alarms: " + feature.properties.alarms, ""];
                text = text.concat(feature.properties.objects.map(function(v) {
                    return "<a target=_ href='/api/card/view/managedobject/" + v.id +"/'>" + v.name + "</a>";
                }));
                layer.bindPopup(text.join("<br/>"));
            }
        },
        popOptions = {
            radius: 3,
            fillColor: "#ff7800",
            color: "#000000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        },
        pointOptions = {
            radius: 5,
            // fillColor: "#000000",
            // color: "#000000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        };
    // @todo: Get maintenance status from URL
    $.ajax("/api/card/view/alarmheat/ajax/?z=" + zoom + "&w=" + w + "&e=" + e + "&n=" + n + "&s=" + s + "&maintenance=" + this.maintenance).done(function(data) {
        // Replace heatmap
        var heat_data = [];
        $.each(data.alarms, function(i, v) {
            if(v.x && v.y && v.w) {
                heat_data.push([v.y, v.x, v.w * 10]);
            }
        });
        //
        if(me.topology) {
            me.map.removeLayer(me.topology);
            me.topology = null;
        }
        if(data.links) {
            me.topology = L.geoJSON(data.links).addTo(me.map);
        }
        //
        if(me.pops) {
            me.map.removeLayer(me.pops);
        }
        if(data.pops) {
            me.pops = L.geoJSON(data.pops, {
                pointToLayer: function(feature, latlng) {
                    if(feature.properties.alarms > 0) {
                        return L.circleMarker(latlng, popOptions)
                    } else {
                        return L.circleMarker(latlng, pointOptions)
                    }
                },
                onEachFeature: onEachPoP
            }).addTo(me.map);
        }
        //
        if(me.heatmap) {
            me.map.removeLayer(me.heatmap);
        }
        me.heatmap = L.heatLayer(heat_data, {radius: 15}).addTo(me.map);
        // Replace summary
        $("#summary").html(data.summary);
        setTimeout(function() {me.poll_data(); }, 60000);
    });
};
