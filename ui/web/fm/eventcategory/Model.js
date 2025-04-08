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
            name: "suppression_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "object_scope",
            type: "string",
            defaultValue: "M"
        },
        {
            name: "required_object",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "object_resolver",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "vars",
            type: "auto"
        },
        {
            name: "resources",
            type: "auto"
        }
    ]
});
