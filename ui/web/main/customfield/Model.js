//---------------------------------------------------------------------
// main.customfield Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfield.Model");

Ext.define("NOC.main.customfield.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/customfield/",

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
            name: "name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "label",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "enum_group",
            type: "string"
        },
        {
            name: "enum_group__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "max_length",
            type: "int",
            defaultValue: 0
        },
        {
            name: "regexp",
            type: "string"
        },
        {
            name: "is_indexed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_searchable",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_filtered",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_hidden",
            type: "boolean",
            defaultValue: false
        }
    ]
});
