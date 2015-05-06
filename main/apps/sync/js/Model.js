//---------------------------------------------------------------------
// main.sync Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.sync.Model");

Ext.define("NOC.main.sync.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/sync/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "n_instances",
            type: "int",
            defaultValue: 1
        },
        {
            name: "user",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
