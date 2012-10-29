//---------------------------------------------------------------------
// inv.macdb Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.Model");

Ext.define("NOC.inv.macdb.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/macdb/",

    fields: [
        {
            name: "managed_object__label",
            type: "string"
        },

        {
            name: "vlan",
            type: "int"
        },
        {
            name: "managed_object",
            type: "int"
        },
        {
            name: "last_changed",
            type: "string"
        },
        {
            name: "mac",
            type: "string"
        },
        {
            name: "interface__label",
            type: "string"
        },
        {
            name: "fav_status",
            type: "auto"
        },
        {
            name: "interface",
            type: "string",
        },
        {
            name: "id",
            type: "string"
        }
    ]
});
