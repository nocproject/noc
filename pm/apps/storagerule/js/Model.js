//---------------------------------------------------------------------
// pm.storagerule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storagerule.Model");

Ext.define("NOC.pm.storagerule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/storagerule/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "xfilesfactor",
            type: "float"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "aggregation_method",
            type: "string",
            defaultValue: "average"
        },
        {
            name: "retentions",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "retention_text",
            type: "string",
            persist: false
        },
        {
            name: "interval",
            type: "string",
            persist: false
        }
    ]
});
