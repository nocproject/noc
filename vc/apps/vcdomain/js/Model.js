//---------------------------------------------------------------------
// vc.vcdomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcdomain.Model");

Ext.define("NOC.vc.vcdomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vcdomain/",

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
            name: "type",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "enable_provisioning",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_vc_bind_filter",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "style",
            type: "int"
        },
        // Foreign keys
        {
            name: "type__label",
            type: "string",
            persist: false
        },
        {
            name: "selector__label",
            type: "string",
            persist: false
        },
        {
            name: "style__label",
            type: "string",
            persist: false
        },
        // Virtual fields
        {
            name: "row_class",
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
