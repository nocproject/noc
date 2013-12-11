//---------------------------------------------------------------------
// inv.objectmodel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Model");

Ext.define("NOC.inv.objectmodel.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/objectmodel/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "vendor",
            type: "string"
        },
        {
            name: "vendor__label",
            type: "string",
            persist: false
        },
        {
            name: "connection_rule",
            type: "string"
        },
        {
            name: "connection_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "connections",
            type: "auto"
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
            name: "data",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
