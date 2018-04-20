//---------------------------------------------------------------------
// gis.layer Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.layer.Model");

Ext.define("NOC.gis.layer.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/layer/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "fill_color",
            type: "auto"
        },
        {
            name: "stroke_color",
            type: "auto"
        },
        {
            name: "default_zoom",
            type: "int"
        },
        {
            name: "max_zoom",
            type: "int"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "min_zoom",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "zindex",
            type: "int"
        },
        {
            name: "stroke_width",
            type: "int"
        },
        {
            name: "point_radius",
            type: "int"
        },
        {
            name: "show_labels",
            type: "boolean"
        },
        {
            name: "stroke_dashstyle",
            type: "string"
        },
        {
            name: "point_graphic",
            type: "string"
        }
    ]
});
