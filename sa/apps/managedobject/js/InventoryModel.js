//---------------------------------------------------------------------
// sa.managedobject InventoryModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.InventoryModel");

Ext.define("NOC.sa.managedobject.InventoryModel", {
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
        }
    ]
});
