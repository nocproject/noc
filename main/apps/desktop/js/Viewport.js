//---------------------------------------------------------------------
// Application Viewport
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Viewport");

Ext.define("NOC.main.desktop.Viewport", {
    extend: "Ext.Viewport",
    layout: "border",
    items: [
        Ext.create("NOC.main.desktop.HeaderPanel"),
        Ext.create("NOC.main.desktop.NavPanel"),
        Ext.create("NOC.main.desktop.WorkplacePanel")
    ]
});
