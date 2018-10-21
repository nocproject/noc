//---------------------------------------------------------------------
// main.chpolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.chpolicy.Model");

Ext.define("NOC.main.chpolicy.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/chpolicy/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "table",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "dry_run",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "ttl",
            type: "int"
        }
    ]
});
