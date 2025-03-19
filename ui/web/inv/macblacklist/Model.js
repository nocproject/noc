//---------------------------------------------------------------------
// inv.macblacklist Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macblacklist.Model");

Ext.define("NOC.inv.macblacklist.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/macblacklist/",

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
            name: "uuid",
            type: "string"
        },
        {
            name: "from_mac",
            type: "string"
        },
        {
            name: "to_mac",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "affected",
            type: "auto"
        },
        {
            name: "is_duplicated",
            type: "boolean"
        },
        {
            name: "is_ignored",
            type: "boolean"
        }
    ]
});