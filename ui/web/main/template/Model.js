//---------------------------------------------------------------------
// main.template Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.template.Model");

Ext.define("NOC.main.template.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/template/",

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
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "subject",
            type: "string"
        },
        {
            name: "body",
            type: "string"
        },
        {
            name: "is_system",
            type: "boolean",
            persist: false
        },
        {
            name: "message_type",
            type: "string"
        },
        {
            name: "language",
            type: "string"
        },
        {
            name: "context_data",
            type: "string"
        }
    ]
});
