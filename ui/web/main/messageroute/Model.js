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
            defaultValue: 10
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
            name: "transmute_handler",
            type: "string"
        },
        {
            name: "transmute_handler__label",
            type: "string",
            persist: false
        },
        {
            name: "transmute_template",
            type: "string"
        },
        {
            name: "transmute_template__label",
            type: "string",
            persist: false
        },
        {
            name: "action",
            type: "string",
            defaultValue: "notification"
        },
        {
            name: "stream",
            type: "string"
        },
        {
            name: "telemetry_sample",
            type: "int",
             defaultValue: 0
        },
        {
            name: "notification_group",
            type: "int"
        },
        {
            name: "notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "render_template",
            type: "string"
        },
        {
            name: "render_template__label",
            type: "string",
            persist: false
        },
        {
            name: "headers",
            type: "auto"
        }
    ]
});