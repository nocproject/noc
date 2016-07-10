//---------------------------------------------------------------------
// sa.action Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.action.Model");

Ext.define("NOC.sa.action.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/action/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "access_level",
            type: "int",
            defaultValue: 15
        },
        {
            name: "uuid",
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
            name: "handler",
            type: "string"
        },
        {
            name: "params",
            type: "auto"
        },
        {
            name: "label",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        }
    ]
});
