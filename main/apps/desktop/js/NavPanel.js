//---------------------------------------------------------------------
// Navigation panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
Ext.define("NOC.main.desktop.NavPanel", {
    extend: "Ext.Panel",
    id: "nav",
    region: "west",
    width: 200,
    collapsible: true,
    animCollapse: true,
    split: true,
    preventHeader: true,
    layout: "accordion",
    items: [
        Ext.create("NOC.main.desktop.NavTree"),
        Ext.create("NOC.main.desktop.Favorites")
    ]
});
