//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.model.Container");

Ext.define("NOC.sa.discoveredobject.model.Container", {
    extend: "Ext.app.ViewModel",
    alias: "viewmodel.sa.discoveredobject.container",

    data: {
        isFilterOpen: true,
    },
});