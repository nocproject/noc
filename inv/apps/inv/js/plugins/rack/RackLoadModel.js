//---------------------------------------------------------------------
// inv.inv RackLoadModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackLoadModel");

Ext.define("NOC.inv.inv.plugins.rack.RackLoadModel", {
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
            name: "units",
            type: "int"
        },
        {
            name: "position_front",
            type: "int"
        },
        {
            name: "position_rear",
            type: "int"
        }
    ]
});
