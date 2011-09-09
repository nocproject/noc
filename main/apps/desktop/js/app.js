//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
Ext.application({
    name: "NOC",
    controllers: ["NOC.main.desktop.Controller"],

    launch: function() {
        console.log("NOC application starting");
        Ext.create("NOC.main.desktop.Viewport");
        console.log("NOC application ready");
    }
});
