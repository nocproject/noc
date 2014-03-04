//---------------------------------------------------------------------
// inv.inv InventoryModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.inventory.InventoryModel");

Ext.define("NOC.inv.inv.plugins.inventory.InventoryModel", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "model",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "serial",
            type: "string"
        },
        {
            name: "revision",
            type: "string"
        }
    ]
});
