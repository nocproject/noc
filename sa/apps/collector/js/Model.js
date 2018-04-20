//---------------------------------------------------------------------
// sa.collector Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.collector.Model");

Ext.define("NOC.sa.collector.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/collector/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
