//---------------------------------------------------------------------
// main.messageroute Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.messageroute.Model");

Ext.define("NOC.main.messageroute.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/messageroute/",

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
        },
        {
            name: "order",
            type: "int",
            defaultValue: 0
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "match",
            type: "auto"
        },
        {
            name: "transmute",
            type: "auto"
        },
        {
            name: "action",
            type: "auto"
        }
    ]
});