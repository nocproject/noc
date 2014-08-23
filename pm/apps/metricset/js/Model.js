//---------------------------------------------------------------------
// pm.metricset Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricset.Model");

Ext.define("NOC.pm.metricset.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metricset/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "metrics",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
