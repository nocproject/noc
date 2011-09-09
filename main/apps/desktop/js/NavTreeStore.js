//---------------------------------------------------------------------
// Navigation tree panel store
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
Ext.define("NOC.main.desktop.NavTreeStore", {
    extend: "Ext.data.TreeStore",
    storeId: "NOC.main.desktop.NavTreeStore",
    
    proxy: {
        type: "ajax",
        url: "/main/desktop/navigation/"
    }
});
