//---------------------------------------------------------------------
// pm.metricscope Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricscope.Model");

Ext.define("NOC.pm.metricscope.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metricscope/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "key_fields",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "table_name",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "enable_timedelta",
            type: "boolean",
            persist: false
        }
    ]
});
