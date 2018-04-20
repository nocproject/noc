//---------------------------------------------------------------------
// main.style Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.style.Model");

Ext.define("NOC.main.style.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/style/",

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
            name: "font_color",
            type: "auto"
        },
        {
            name: "background_color",
            type: "auto"
        },
        {
            name: "bold",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "italic",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "underlined",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
