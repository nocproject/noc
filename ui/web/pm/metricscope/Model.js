//---------------------------------------------------------------------
// pm.metricscope Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
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
            type: "string"
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
            name: "path",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
