//---------------------------------------------------------------------
// sa.objectdiscoveryrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectdiscoveryrule.Model");

Ext.define("NOC.sa.objectdiscoveryrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/objectdiscoveryrule/",

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
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "network_ranges",
            type: "auto"
        },
        {
            name: "checks",
            type: "auto"
        },
        {
            name: "sources",
            type: "auto"
        },
        {
            name: "network_ranges",
            type: "auto"
        },
        {
            name: "conditions",
            type: "auto"
        },
        {
            name: "preference",
            type: "int",
            defaultValue: 100
        },
        {
            name: "update_interval",
            type: "int",
            defaultValue: 300
        },
        {
            name: "expired_ttl",
            type: "int",
            defaultValue: 0
        },
        {
            name: "default_action",
            type: "string"
        },
        {
            name: "sync_approved",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_ip_scan_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "ip_scan_discovery_interval",
            type: "int",
            defaultValue: 0
        },
        {
            name: "default_template",
            type: "string"
        }
    ]
});
