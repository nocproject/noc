//---------------------------------------------------------------------
// pm.metricsettings Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricsettings.Model");

Ext.define("NOC.pm.metricsettings.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metricsettings/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "model_id",
            type: "string"
        },
        {
            name: "object_id",
            type: "string"
        },
        {
            name: "metric_sets",
            type: "auto",
            defaultValue: <function <lambda> at 0x110099de8>
        }
    ]
});
