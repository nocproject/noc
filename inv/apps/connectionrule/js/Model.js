//---------------------------------------------------------------------
// inv.connectionrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectionrule.Model");

Ext.define("NOC.inv.connectionrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/connectionrule/",

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
            name: "rules",
            type: "auto"
        },
        {
            name: "context",
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
