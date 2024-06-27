//---------------------------------------------------------------------
// sa.discoveredobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.Model");

Ext.define("NOC.sa.discoveredobject.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/discoveredobject/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "address",
            type: "string",
            persist: false
        },
        {
            name: "pool",
            type: "string"
        },
        {
            name: "pool__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string",
            persist: false
        },
        {
            name: "hostname",
            type: "string",
            persist: false
        },
        {
            name: "chassis_id",
            type: "string",
            persist: false
        },
        {
            name: "uptime",
            type: "int",
            persist: false
        },
        {
            name: "state",
            type: "string"
        },
        {
            name: "state__label",
            type: "string",
            persist: false
        },
        {
            name: "last_seen",
            type: "auto",
            persist: false
        },
        {
            name: "first_discovered",
            type: "auto",
            persist: false
        },
        {
            name: "is_dirty",
            type: "bool",
            persist: false
        },
        {
            name: "managed_object",
            type: "int"
        },
        {
            name: "managed_object__label",
            type: "string",
            persist: false
        },
        {
            name: "agent",
            type: "string"
        },
        {
            name: "agent__label",
            type: "string",
            persist: false
        },
        {
            name: "rule",
            type: "string"
        },
        {
            name: "rule__label",
            type: "string",
            persist: false
        },
        {
            name: "checks",
            type: "auto",
            persist: false
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "effective_labels",
            type: "auto",
            persist: false
        }
    ]
});
