//----------------------------------------------------------------------
//  Alarm heatmap
//----------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------
var Heatmap = function () {
    this.map = null;
};

Heatmap.prototype.initialize = function () {
    var q = this.parseQuerystring(),
        lon = q.lon ? parseFloat(q.lon) : 37.5077,
        lat = q.lat ? parseFloat(q.lat) : 55.7766,
        scale = q.zoom ? parseInt(q.zoom) : 11;
    this.map = L.map("map");
    this.heatmap = null;
    // Set up OSM layer
    var osm = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        });
    this.map.addLayer(osm);
    // Select view
    this.map.setView([lat, lon], scale);
    // Poll data
    this.poll_data();
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

Heatmap.prototype.run = function () {
    this.initialize();
};

Heatmap.prototype.poll_data = function () {
    var me = this;
    $.ajax("/api/card/view/alarmheat/ajax/").done(function(data) {
        // Replace heatmap
        var heat_data = [];
        $.each(data.alarms, function(i, v) {
            if(v.x && v.y && v.w) {
                heat_data.push([v.y, v.x, v.w * 10]);
            }
        });
        if(me.heatmap) {
            me.map.removeLayer(me.heatmap);
        }
        me.heatmap = L.heatLayer(heat_data, {radius: 15}).addTo(me.map);
        // Replace summary
        $("#summary").html(data.summary);
        setTimeout(function() {me.poll_data(); }, 60000);
    });
};
