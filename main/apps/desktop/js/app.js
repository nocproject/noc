//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");

Ext.application({
    name: "NOC",

    launch: function() {
        var me = this;
        console.log("Initializing history API");
        Ext.History.init();
        console.log("NOC application starting");
        // Create viewport
        me.app = Ext.create("NOC.main.desktop.Application");
    }
});
