//---------------------------------------------------------------------
// ip.prefix Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefix.Model");

Ext.define("NOC.ip.prefix.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/prefix/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "parent",
            type: "int"
        },
        {
            name: "parent__label",
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
            name: "prefix",
            type: "string"
        },
        {
            name: "asn",
            type: "int"
        },
        {
            name: "asn__label",
            type: "string",
            persist: false
        },
        {
            name: "vc",
            type: "int"
        },
        {
            name: "vc__label",
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
        },
        {
            name: "last_changed",
            type: "date"
        },
        {
            name: "last_changed_by",
            type: "string"
        }
    ]
});
