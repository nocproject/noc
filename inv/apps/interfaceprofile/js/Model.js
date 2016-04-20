//---------------------------------------------------------------------
// inv.interfaceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Model");

Ext.define("NOC.inv.interfaceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/interfaceprofile/",

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
            name: "style",
            type: "int"
        },
        {
            name: "link_events",
            type: "string",
            defaultValue: "A"
        },
        {
            name: "mac_discovery",
            type: "bool",
            defaultValue: false
        },
        {
            name: "weight",
            type: "int"
        },
        {
            name: "discovery_policy",
            type: "string"
        },
        {
            name: "status_change_notification",
            type: "string"
        },
        {
            name: "status_change_notification__label",
            type: "string",
            persist: false
        },
        {
            name: "metrics",
            type: "auto"
        },
        // CSS
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        // Foreign keys
        {
            name: "style__label",
            type: "string",
            persist: false
        }
    ]
});
