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
            name: "tags",
            type: "auto"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "enable_prefix_discovery",
            type: "boolean"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "enable_ip_ping_discovery",
            type: "boolean"
        },
        {
            name: "enable_ip_discovery",
            type: "boolean"
        },
        {
            name: "bi_id",
            type: "int"
        },
        {
            name: "autocreated_prefix_profile",
            type: "string"
        },
        {
            name: "autocreated_prefix_profile__label",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
