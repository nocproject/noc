//---------------------------------------------------------------------
// inv.inv LogModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.log.LogModel");

Ext.define("NOC.inv.inv.plugins.log.LogModel", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "ts",
            type: "date"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "system",
            type: "auto"
        },
        {
            name: "managed_object",
            type: "string"
        },
        {
            name: "op",
            type: "string"
        },
        {
            name: "message",
            type: "string"
        }
    ]
});
