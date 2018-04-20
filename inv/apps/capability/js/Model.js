//---------------------------------------------------------------------
// inv.capability Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.capability.Model");

Ext.define("NOC.inv.capability.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/capability/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "type",
            type: "string"
        }
    ]
});
