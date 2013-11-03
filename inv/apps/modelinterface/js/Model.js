//---------------------------------------------------------------------
// inv.modelinterface Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelinterface.Model");

Ext.define("NOC.inv.modelinterface.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/modelinterface/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean"
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
            name: "attrs",
            type: "auto"
        }
    ]
});
