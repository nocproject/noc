//---------------------------------------------------------------------
// inv.inv NavModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.NavModel");

Ext.define("NOC.inv.inv.NavModel", {
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
            name: "plugins",
            type: "auto"
        }
    ]
});
