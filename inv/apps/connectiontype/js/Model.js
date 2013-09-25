//---------------------------------------------------------------------
// inv.connectiontype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectiontype.Model");

Ext.define("NOC.inv.connectiontype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/connectiontype/",

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
            name: "extend",
            type: "string",
            defaultValue: null,
            useNull: true
        },
        {
            name: "multi_connection",
            type: "boolean"
        },
        {
            name: "has_gender",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "data",
            type: "auto"
        },
        {
            name: "c_group",
            type: "auto"
        },
        {
            name: "is_builtin",
            type: "boolean"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
