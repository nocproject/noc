//---------------------------------------------------------------------
// gis.area Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.area.Model");

Ext.define("NOC.gis.area.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/area/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "NE",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "SW",
            type: "auto"
        },
        {
            name: "min_zoom",
            type: "int",
            defaultvalue: 0
        },
        {
            name: "max_zoom",
            type: "int",
            defaultValue: 18
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
