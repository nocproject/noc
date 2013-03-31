//---------------------------------------------------------------------
// main.stompaccess Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.stompaccess.Model");

Ext.define("NOC.main.stompaccess.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/stompaccess/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "prefix_table",
            type: "int"
        },
        {
            name: "prefix_table__label",
            type: "string",
            persist: false
        },
        {
            name: "user",
            type: "string"
        }
    ]
});
