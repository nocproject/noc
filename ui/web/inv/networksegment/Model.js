//---------------------------------------------------------------------
// inv.networksegment Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.Model");

Ext.define("NOC.inv.networksegment.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/networksegment/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "parent__label",
            type: "string",
            persist: false
        },
        {
            name: "settings",
            type: "auto"
        },
        {
            name: "sibling",
            type: "string"
        },
        {
            name: "sibling__label",
            type: "string",
            persist: false
        },
        {
            name: "count",
            type: "integer",
            persist: false
        },
        {
            name: "is_redundant",
            type: "boolean",
            persist: false
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "max_shown_downlinks",
            type: "integer",
            defaultValue: 1000
        },
        {
            name: "max_objects",
            type: "integer",
            defaultValue: 300
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
            name: "horizontal_transit_policy",
            type: "string"
        },
        {
            name: "enable_horizontal_transit",
            type: "boolean"
        },
        {
            name: "vlan_border",
            type: "boolean"
        },
        {
            name: "vlan_translation",
            type: "auto"
        },
        {
            name: "allocation_group",
            type: "string"
        },
        {
            name: "allocation_group__label",
            type: "string",
            persist: false
        },
        {
            name: "l2_domain",
            type: "string"
        },
        {
            name: "l2_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "l2_mtu",
            type: "int"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
