//---------------------------------------------------------------------
// fm.eventcategory Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.eventcategory.Model");

Ext.define("NOC.fm.eventcategory.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/eventcategory/",

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
            name: "name",
            type: "string"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
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
            name: "level",
            type: "integer"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "vars",
            type: "auto"
        }
    ]
});
