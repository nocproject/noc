//---------------------------------------------------------------------
// sa.groupaccess Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.groupaccess.Model");

Ext.define("NOC.sa.groupaccess.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/groupaccess/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "group",
            type: "int"
        },
        {
            name: "group__label",
            type: "string",
            persist: false
        },
        {
            name: "selector",
            type: "int"
        },
        {
            name: "selector__label",
            type: "string",
            persist: false
        }
    ]
});
