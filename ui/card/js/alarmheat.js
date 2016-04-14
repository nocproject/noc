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
    this.map = L.map("map");
    this.heatmap = null;
    // Set up OSM layer
    var osm = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {

        });
    this.map.addLayer(osm);
    // Select view
    // @todo: Calculate dynamically
    this.map.setView([55.7766, 37.5077], 11);
    // Poll data
    this.poll_data();
};

Heatmap.prototype.run = function () {
    this.initialize();
};

Heatmap.prototype.poll_data = function () {
    var me = this;
    $.ajax("/api/card/view/alarmheat/ajax/").done(function(data) {
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
        setTimeout(function() {me.poll_data(); }, 60000);
    });
};
