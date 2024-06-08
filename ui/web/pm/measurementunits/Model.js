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
            name: "code",
            type: "string"
        },
        {
            name: "base_unit",
            type: "string"
        },
        {
            name: "base_unit__label",
            type: "string",
            persist: false
        },
        {
            name: "dashboard_label",
            type: "string"
        },
        {
            name: "dashboard_sr_color",
            type: "auto"
        },
        {
            name: "convert_from",
            type: "auto"
        },
        {
            name: "enum",
            type: "auto"
        }
    ]
});