//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");
Ext.require("NOC.main.desktop.Viewport");

Ext.application({
    name: "NOC",
    controllers: ["NOC.main.desktop.Controller"],

    launch: function() {
        console.log("NOC application starting");
        Ext.create("NOC.main.desktop.Viewport");
        console.log("NOC application ready");
    }
});
