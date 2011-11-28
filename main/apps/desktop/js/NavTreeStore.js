//---------------------------------------------------------------------
// Navigation tree panel store
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavTreeStore");

Ext.define("NOC.main.desktop.NavTreeStore", {
    extend: "Ext.data.TreeStore",
    storeId: "NOC.main.desktop.NavTreeStore",

    proxy: {
        type: "ajax",
        url: "/main/desktop/navigation/",
        destroy: Ext.emptyFn,
        create: Ext.emptyFn,
        update: Ext.emptyFn
    }
});
