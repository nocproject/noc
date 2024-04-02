//---------------------------------------------------------------------
// sa.serviceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Model");

Ext.define("NOC.sa.serviceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/serviceprofile/",

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
            name: "card_title_template",
            type: "string"
        },
        {
            name: "glyph",
            type: "string"
        },
        {
            name: "display_order",
            type: "integer",
            defaultValue: 100
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "interface_profile",
            type: "string"
        },
        {
            name: "weight",
            type: "int"
        },
        {
            name: "status_transfer_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "status_transfer_function",
            type: "string",
            defaultValue: "MIN"
        },
        {
            name: "alarm_affected_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "show_in_summary",
            type: "boolean"
        },
        {
            name: "interface_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "caps",
            type: "auto"
        },
        {
            name: "status_transfer_rule",
            type: "auto"
        },
        {
            name: "status_transfer_map",
            type: "auto"
        },
        {
            name: "alarm_filter",
            type: "auto"
        },
        {
            name: "alarm_status_map",
            type: "auto"
        }
    ]
});
