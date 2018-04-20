//---------------------------------------------------------------------
// fm.alarmseverity Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmseverity.Model");

Ext.define("NOC.fm.alarmseverity.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmseverity/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "severity",
            type: "int"
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
            name: "name",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
