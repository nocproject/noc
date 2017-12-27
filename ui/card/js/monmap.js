//----------------------------------------------------------------------
//  Monmap
//----------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------
var Monmap = function() {
    this.map = null;
};

Monmap.prototype.initialize = function(lon, lat, zoom) {
    var me = this,
        q = this.parseQuerystring(),
        lon = q.lon ? parseFloat(q.lon) : lon || 135.656987,
        lat = q.lat ? parseFloat(q.lat) : lat || 55.005569,
        scale = q.zoom ? parseInt(q.zoom) : zoom || 5;
    // lon = q.lon ? parseFloat(q.lon) : lon || 37.5077,
    // lat = q.lat ? parseFloat(q.lat) : lat || 55.7766,
    // scale = q.zoom ? parseInt(q.zoom) : zoom || 11;
    this.map = L.map("map");
    // Set up OSM layer
    var osm = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {});
    this.map.addLayer(osm);
    // Select view, trigger moveend to poll data
    this.map.setView([lat, lon], scale);
    // Init markerCluster
    // doc: https://github.com/Leaflet/Leaflet.markercluster
    this.markers = L.markerClusterGroup({
        chunkedLoading: true,
        iconCreateFunction: function(cluster) {
            var childCount = cluster.getChildCount();
            var errors = cluster.getAllChildMarkers().reduce(function(a, b) {
                return a + b.options.error
            }, 0);

            if(errors > 0) {
                return new L.DivIcon({
                    html: '<div><span>' + errors + '</span></div>',
                    className: 'marker-cluster marker-cluster-error',
                    iconSize: new L.Point(40, 40)
                });
            }

            var warnings = cluster.getAllChildMarkers().reduce(function(a, b) {
                return a + b.options.warning
            }, 0);
            if(warnings > 0) {
                return new L.DivIcon({
                    html: '<div><span>' + warnings + '</span></div>',
                    className: 'marker-cluster marker-cluster-warning',
                    iconSize: new L.Point(40, 40)
                });
            }

            var goods = cluster.getAllChildMarkers().reduce(function(a, b) {
                return a + b.options.good
            }, 0);
            return new L.DivIcon({
                html: '<div><span>' + goods + '</span></div>',
                className: 'marker-cluster marker-cluster-good',
                iconSize: new L.Point(40, 40)
            });
        }
        // spiderfyOnMaxZoom: false,
        // showCoverageOnHover: false,
        // zoomToBoundsOnClick: false
    });
    me.poll_data();
};

Monmap.prototype.parseQuerystring = function() {
    var q = window.location.search.substring(1),
        vars = q.split("&"),
        r = {}, i, pair;
    for(i = 0; i < vars.length; i++) {
        pair = vars[i].split("=");
        r[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
    }
    return r;
};

Monmap.prototype.run = function(maintenance, lon, lat, zoom) {
    this.maintenance = maintenance;
    this.initialize(lon, lat, zoom);
};

Monmap.prototype.poll_data = function() {
    var me = this,
        bbox = me.map.getBounds(),
        w = bbox.getWest(),
        e = bbox.getEast(),
        n = bbox.getNorth(),
        s = bbox.getSouth(),
        zoom = me.map.getZoom();

    $("#summary").html('<i class="fa fa-spinner fa-spin"></i>' + "Loading ...");
    // $.getJSON( "/ui/card/js/data.json", function( data ) { // test
    $.ajax("/api/card/view/monmap/ajax/?z=" + zoom + "&w=" + w + "&e=" + e + "&n=" + n + "&s=" + s + "&maintenance=" + this.maintenance).done(function(data) {
        me.markers.clearLayers();
        for(var i = 0; i < data.objects.length; i++) {
            var a = data.objects[i];
            var color, fillColor;
            var title = a.name + "</br>error:" + a.error + "</br>warning: " + a.warning;
            var markerOptions = {
                title: title,
                error: a.error,
                warning: a.warning,
                good: a.good,
                fillOpacity: 0.6,
                opacity: 1,
                weight: 3
            };

            if(a.error) {
                color = "#FF0000";
                fillColor = "#FF4500";
            } else if(a.warning) {
                color = "#F0C20C";
                fillColor = "#FFFF00";
            } else {
                color = "#6ECC39";
                fillColor = "#B5E28C";
            }
            markerOptions.fillColor = fillColor;
            markerOptions.color = color;

            var marker = L.circleMarker(L.latLng(a.y, a.x), markerOptions);
            marker.bindPopup(title);
            me.markers.addLayer(marker);
        }
        me.map.addLayer(me.markers);
        $("#summary").html("");
        setTimeout(function() {me.poll_data(); }, 60000);
    });
};
