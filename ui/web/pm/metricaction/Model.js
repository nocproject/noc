//---------------------------------------------------------------------
// pm.metricaction Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricaction.Model");

Ext.define("NOC.pm.metricaction.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metricaction/",

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
            name: "description",
            type: "string"
        },
        {
            name: "metric_type",
            type: "string"
        },
        {
            name: "metric_type__label",
            type: "string",
            persist: false
        },
        {
            name: "actions",
            type: "auto"
        },
        {
            name: "params",
            type: "auto"
        },
    ]
});
