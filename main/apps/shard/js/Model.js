//---------------------------------------------------------------------
// main.shard Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.shard.Model");

Ext.define("NOC.main.shard.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/shard/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },

        {
            name: "description",
            type: "string"
        }
    ]
});
