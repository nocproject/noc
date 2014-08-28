//---------------------------------------------------------------------
// pm.probe Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.probe.Model");

Ext.define("NOC.pm.probe.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/probe/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "user",
            type: "integer"
        },
        {
            name: "user__label",
            type: "string",
            persist: false
        }
    ]
});
