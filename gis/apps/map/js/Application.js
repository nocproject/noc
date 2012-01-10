//---------------------------------------------------------------------
// gis.map application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.map.Application");

Ext.define("NOC.gis.map.Application", {
    extend: "NOC.core.Application",
    //requires: [],

    initComponent: function() {
        Ext.Ajax.request({
            method: "GET",
            url: "/gis/map/layers/",
            scope: this,
            success: function(response) {
                console.log(Ext.decode(response.responseText));
            }
        });
    }
});
