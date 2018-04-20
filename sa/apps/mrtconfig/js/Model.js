//---------------------------------------------------------------------
// sa.mrtconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.mrtconfig.Model");

Ext.define("NOC.sa.mrtconfig.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/mrtconfig/",

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
            name: "permission_name",
            type: "string"
        },
        {
            name: "timeout",
            type: "int"
        },
        {
            name: "map_script",
            type: "string"
        },
        {
            name: "reduce_pyrule",
            type: "int"
        },
        {
            name: "reduce_pyrule__label",
            type: "string",
            persist: false
        },
        {
            name: "selector",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
