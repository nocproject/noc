//---------------------------------------------------------------------
// pm.ts Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.Model");

Ext.define("NOC.pm.ts.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/ts/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "ts_id",
            type: "int"
        },
        {
            name: "storage",
            type: "string"
        },
        {
            name: "storage__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "check",
            type: "string"
        },
        {
            name: "check__label",
            type: "string",
            persist: false
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "type",
            type: "string"
        }
    ]
});
