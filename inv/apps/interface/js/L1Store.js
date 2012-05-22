//---------------------------------------------------------------------
// inv.interface L1 Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L1Store");

Ext.define("NOC.inv.interface.L1Store", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "name",
            type: "string"
        },
        {
            name: "mac",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "ifindex",
            type: "int"
        }
    ],
    data: []
});
