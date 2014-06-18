//---------------------------------------------------------------------
// Navigation tree panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavTree");

Ext.define("NOC.main.desktop.NavTree", {
    extend: "Ext.tree.Panel",
    id: "navtree",
    title: "Navigation",
    glyph: NOC.glyph.globe,
    useArrows: true,
    rootVisible: false,
    singleExpand: true,
    store: Ext.create("NOC.main.desktop.NavTreeStore")
});
