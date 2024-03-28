//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.controller.Grid");

Ext.define("NOC.sa.discoveredobject.controller.Grid", {
    extend: "Ext.app.ViewController",
    alias: "controller.sa.discoveredobject.grid",

    checksRenderer: function(v) {
        var result = [];
        Ext.Array.each(v, function(item) {
            var text = item.label + (item.port ? ":" + item.port : ""),
                background = "background:" + (item.status ? "lightgreen;" : "goldenrod;"),
                border = "border:" + (item.status ? "green" : "red") + " 1px solid;";

            result.push("<span style='" + border + background + "padding:1;margin:2;'>" + text + "</span>");
        });
        return result.join("") || __("N/A");
    },
    afterrenderHandler: function(grid) {
        grid.up().lookup("sa-discovered-sidebar").getController().reload();
    },
});
