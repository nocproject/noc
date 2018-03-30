//---------------------------------------------------------------------
// sa.administrativedomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.Model");

Ext.define("NOC.sa.administrativedomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/administrativedomain/",

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
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
