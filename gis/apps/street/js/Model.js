//---------------------------------------------------------------------
// gis.division Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.street.Model");

Ext.define("NOC.gis.street.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/street/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "end_date",
            type: "date"
        },
        {
            name: "short_name",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "parent__label",
            type: "string"
        },
        {
            name: "full_parent",
            type: "string",
            persist: false
        },
        {
            name: "full_path",
            type: "string",
            persist: false
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "data",
            type: "auto"
        },
        {
            name: "start_date",
            type: "date"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
