//---------------------------------------------------------------------
// sa.activator Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.activator.Model");

Ext.define("NOC.sa.activator.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/activator/",

    fields: [
        {
            name: "id",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "shard",
            type: "int"
        },
        {
            name: "shard__label",
            type: "string",
            persist: false
        },
        {
            name: "prefix_table",
            type: "int"
        },
        {
            name: "prefix_table__label",
            type: "string",
            persist: false
        },
        {
            name: "auth",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
