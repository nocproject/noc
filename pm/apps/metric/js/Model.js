//---------------------------------------------------------------------
// pm.metric Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metric.Model");

Ext.define("NOC.pm.metric.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metric/",

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
            name: "hash",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        }
    ]
});
