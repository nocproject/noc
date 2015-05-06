//---------------------------------------------------------------------
// sa.actioncommands Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.actioncommands.Model");

Ext.define("NOC.sa.actioncommands.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/actioncommands/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "commands",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "action",
            type: "string"
        },
        {
            name: "match",
            type: "auto"
        },
        {
            name: "config_mode",
            type: "boolean"
        },
        {
            name: "preference",
            type: "integer"
        },
        {
            name: "timeout",
            type: "integer"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        }
    ]
});
