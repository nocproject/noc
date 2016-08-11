//---------------------------------------------------------------------
// sa.administrativedomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.Model");

Ext.define("NOC.sa.administrativedomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/administrativedomain/",

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
            name: "description",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "parent__label",
            type: "string",
            persist: false
        },
        {
            name: "default_pool",
            type: "string"
        },
        {
            name: "default_pool__label",
            type: "string",
            persist: false
        },
        {
            name: "object_count",
            type: "int",
            persist: false
        }
    ]
});
