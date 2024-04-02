//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.ApplicationController");

Ext.define("NOC.sa.discoveredobject.ApplicationController", {
    extend: "Ext.app.ViewController",
    alias: "controller.sa.discoveredobject",

    onAfterRender: function(panel) {
        panel.lookup("sa-discoveredobject-list").lookup("sa-discovered-sidebar").getController().restoreFilter();
    },
});
