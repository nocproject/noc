//---------------------------------------------------------------------
// pm.measurementunits Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.measurementunits.Model");

Ext.define("NOC.pm.measurementunits.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/measurementunits/",

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
            name: "uuid",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "label",
            type: "string"
        },
        {
            name: "dashboard_label",
            type: "string"
        },
        {
            name: "scale_type",
            type: "string",
            defaultValue: "d"
        },
        {
            name: "alt_units",
            type: "auto"
        },
        {
            name: "enum",
            type: "auto"
        }
    ]
});