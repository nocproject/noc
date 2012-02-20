//---------------------------------------------------------------------
// main.pyrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.Model");

Ext.define("NOC.main.pyrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/pyrule/",

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
            name: "interface",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "text",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            defaultValue: false
        }
    ]
});
