//---------------------------------------------------------------------
// inv.inv DataModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.data.DataModel");

Ext.define("NOC.inv.inv.plugins.data.DataModel", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "interface",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "value",
            type: "auto"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "is_const",
            type: "boolean"
        }
    ]
});
