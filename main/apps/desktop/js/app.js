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
        // Set unload handler
        Ext.EventManager.addListener(window, "beforeunload",
            me.onUnload, me, {normalized: false});
        // Create viewport
        me.app = Ext.create("NOC.main.desktop.Application");
    },
    //
    onUnload: function(e) {
        var me = this,
            msg = "You're trying to close NOC application. Unsaved changes may be lost.";
        if(e) {
            e.returnValue = msg;
        }
        if(window.event) {
            window.event.returnValue = msg;
        }
        return msg;
    }
});
