//---------------------------------------------------------------------
// inv.unknownmodel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.unknownmodel.Model");

Ext.define("NOC.inv.unknownmodel.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/unknownmodel/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "part_no",
            type: "string"
        },
        {
            name: "vendor",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "managed_object",
            type: "string"
        }
    ]
});
