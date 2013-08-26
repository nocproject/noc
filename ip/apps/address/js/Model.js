//---------------------------------------------------------------------
// ip.address Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.address.Model");

Ext.define("NOC.ip.address.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/address/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "prefix",
            type: "int"
        },
        {
            name: "prefix__label",
            type: "string",
            persist: false
        },
        {
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "afi",
            type: "string"
        },
        {
            name: "address",
            type: "string"
        },
        {
            name: "fqdn",
            type: "string"
        },
        {
            name: "mac",
            type: "string"
        },
        {
            name: "auto_update_mac",
            type: "boolean",
            defaultValue: false
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
            name: "description",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "tt",
            type: "int"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "style__label",
            type: "string",
            persist: false
        },
        {
            name: "state",
            type: "int"
        },
        {
            name: "state__label",
            type: "string",
            persist: false
        },
        {
            name: "allocated_till",
            type: "date"
        },
        {
            name: "ipv6_transition",
            type: "int"
        },
        {
            name: "ipv6_transition__label",
            type: "string",
            persist: false
        }
    ]
});
