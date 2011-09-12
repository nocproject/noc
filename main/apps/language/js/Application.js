//---------------------------------------------------------------------
// main.language application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.language.Application");

Ext.require("NOC.main.language.Model");
var store = Ext.create("Ext.data.Store", {
    model: "NOC.main.language.Model",
    autoLoad: true,
    autoSync: true,
    pageSize: 10
});

console.debug("Store for NOC.main.language.Model initialized");

Ext.define("NOC.main.language.Application", {
    extend: "Ext.grid.Panel",
    store: store,
    columns: [
        {text: "Name", dataIndex: "name"},
        {text: "Native Name", dataIndex: "native_name"},
        {text: "Active", dataIndex: "is_active"}
    ],
    dockedItems: [{
            xtype: "pagingtoolbar",
            store: store,
            dock: "bottom",
            displayInfo: true
    }]
});
