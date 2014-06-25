//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");

Ext.application({
    name: "NOC",
    controllers: ["NOC.main.desktop.Controller"],

    launch: function() {
        var me = this;
        console.log("Initializing history API");
        Ext.History.init();
        console.log("NOC application starting");
        var controller = me.controllers.first();
        NOC.run = controller.launchTab;
        NOC.launch = Ext.bind(controller.launchApp, controller);
        // Set unload handler
        Ext.EventManager.addListener(window, "beforeunload",
            me.onUnload, me, {normalized: false});
        // Create viewport
        console.log("Creating viewport");
        Ext.create("Ext.Viewport", {
            layout: "border",
            items: [
                Ext.create("NOC.main.desktop.HeaderPanel"),
                Ext.create("NOC.main.desktop.NavPanel"),
                Ext.create("NOC.main.desktop.WorkplacePanel")
            ],
            listeners: {
                scope: me,
                afterrender: me.onViewportRendered
            }
        });
    },
    // Viewport is rendered, launch application from history
    onViewportRendered: function() {
        var h = Ext.History.getHash();
        console.log("NOC application ready");
        if(h) {
            // Open application tab
            var p = h.split("/"),
                app = p[0],
                args = p.slice(1);
            if(args.length > 0) {
                NOC.launch(app, "history", {args: args});
            } else {
                NOC.launch(app);
            }
        }
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
