//---------------------------------------------------------------------
// main.label Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.label.Model");

Ext.define("NOC.main.label.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/label/",

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
            name: "description",
            type: "string"
        },
        {
            name: "bg_color1",
            type: "int"
        },
        {
            name: "fg_color1",
            type: "int",
            defaultValue: 16777215
        },
        {
            name: "bg_color2",
            type: "int"
        },
        {
            name: "fg_color2",
            type: "int",
            defaultValue: 16777215
        },
        {
            name: "enable_agent",
            type: "boolean"
        },
        {
            name: "enable_service",
            type: "boolean"
        },
        {
            name: "expose_metric",
            type: "boolean"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_id",
            type: "string"
        }
    ]
});