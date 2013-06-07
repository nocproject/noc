//---------------------------------------------------------------------
// pm.check Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.Model");

Ext.define("NOC.pm.check.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/check/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "interval",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "storage",
            type: "string"
        },
        {
            name: "storage__label",
            type: "string",
            persist: false
        },
        {
            name: "probe",
            type: "string"
        },
        {
            name: "probe__label",
            type: "string",
            persist: false
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "check",
            type: "string"
        }
    ]
});
