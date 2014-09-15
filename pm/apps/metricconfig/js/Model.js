//---------------------------------------------------------------------
// pm.metricconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricconfig.Model");

Ext.define("NOC.pm.metricconfig.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metricconfig/",

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
            name: "storage_rule",
            type: "string"
        },
        {
            name: "storage_rule__label",
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
            name: "metrics",
            type: "auto"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "config",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
