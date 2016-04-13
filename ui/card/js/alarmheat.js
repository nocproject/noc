//----------------------------------------------------------------------
//  Alarm heatmap
//----------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

heatmap = {
    map: null,
    create: function() {
        this.map = L.map("map");
        // Select view
        // @todo: Calculate dynamically
        this.map.setView([55.7766, 37.5077], 11);
        // Set up OSM layer
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {}).addTo(this.map);
    },
    run: function() {
        this.create()
    }
};
