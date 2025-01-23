//---------------------------------------------------------------------
// ip.prefixprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixprofile.Model");

Ext.define("NOC.ip.prefixprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/prefixprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "prefix_discovery_policy",
            type: "string",
            defaultValue: "D"
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
            name: "pools",
            type: "auto"
        },
        {
            name: "address_discovery_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "default_address_profile",
            type: "string"
        },
        {
            name: "enable_ip_ping_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "bi_id",
            type: "int"
        },
        {
            name: "name_template",
            type: "string"
        },
        {
            name: "name_template__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "seen_propagation_policy",
            type: "string",
            defaultValue: "P"
        },
        {
            name: "prefix_special_address_policy",
            type: "string",
            defaultValue: "X"
        }
    ]
});
